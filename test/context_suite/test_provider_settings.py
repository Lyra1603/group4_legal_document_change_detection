"""Protect the mixed binding's credential routing and provider probe contract."""
from base64 import b64encode
import json
from pathlib import Path
from struct import pack
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import httpx

from backend.app.context.chunk_builder import build_chunks, pack_adjacent_chunks
from backend.app.context.source_registry import SourceRegistry
from backend.app.context.owned_server import OwnedLightRAG, read_provider_env
from backend.app.context.provider_settings import check_groq_jina, provider_environment
from backend.app.context.lightrag_client import RetrievalError, _index_failure_code


SETTINGS = {
    'LEGAL_AI_PROVIDER': 'groq-jina',
    'GROQ_API_KEY': 'groq-test-key',
    'GROQ_MODEL': 'qwen/qwen3.8-27b',
    'JINA_API_KEY': 'jina-test-key',
    'JINA_EMBEDDING_MODEL': 'jina-embeddings-v4',
    'JINA_EMBEDDING_DIM': '2048',
    'OPENAI_API_KEY': 'unrelated-key',
}


class ProviderSettingsTests(unittest.TestCase):
    def test_container_receives_independent_bindings_and_explicit_limits(self):
        def fake_docker(args, **_):
            if args[0] == 'run':
                path = Path(args[args.index('--env-file') + 1])
                config = dict(line.split('=', 1) for line in path.read_text().splitlines())
                self.assertEqual(config['LLM_BINDING'], 'openai')
                self.assertEqual(config['LLM_BINDING_HOST'], 'https://api.groq.com/openai/v1')
                self.assertEqual(config['LLM_BINDING_API_KEY'], SETTINGS['GROQ_API_KEY'])
                self.assertEqual(config['EMBEDDING_BINDING'], 'jina')
                self.assertEqual(config['EMBEDDING_BINDING_HOST'], 'https://api.jina.ai/v1/embeddings')
                self.assertEqual(config['EMBEDDING_BINDING_API_KEY'], SETTINGS['JINA_API_KEY'])
                self.assertEqual(config['MAX_GLEANING'], '0')
                self.assertNotIn(SETTINGS['OPENAI_API_KEY'], config.values())
                self.assertNotIn(config['LIGHTRAG_API_KEY'], (SETTINGS['GROQ_API_KEY'], SETTINGS['JINA_API_KEY']))
            return '127.0.0.1:29999' if args[0] == 'port' else 'sha256:fake-image'

        with (
            TemporaryDirectory() as temp,
            patch('backend.app.context.owned_server.docker', side_effect=fake_docker),
            patch('backend.app.context.owned_server.LightRAGClient.verify_server'),
        ):
            server = OwnedLightRAG(temp, 'a' * 32, SETTINGS)
            client = server.start()
            try:
                self.assertFalse((server.directory / '.env').exists())
                self.assertEqual(client.config.max_chunks, 12)
                self.assertEqual(server.profile['embedding_provider'], 'jina')
                self.assertFalse(any(key in json.dumps(server.profile) for key in
                                     (SETTINGS['GROQ_API_KEY'], SETTINGS['JINA_API_KEY'])))
            finally:
                client.close()

    def test_missing_jina_key_does_not_fall_back_to_openai(self):
        with self.assertRaisesRegex(RetrievalError, 'REAL_SERVICE_CONFIGURATION_REQUIRED'):
            provider_environment({**SETTINGS, 'JINA_API_KEY': ''})

    def test_explicit_profile_file_takes_precedence(self):
        with TemporaryDirectory() as temp, patch.dict('os.environ', {'LEGAL_AI_PROVIDER': 'openai'}):
            path = Path(temp) / '.env'
            path.write_text('LEGAL_AI_PROVIDER=groq-jina\n', encoding='utf-8')
            self.assertEqual(read_provider_env(path)['LEGAL_AI_PROVIDER'], 'groq-jina')

    def test_probes_validate_response_and_use_only_the_matching_key(self):
        def respond(request):
            payload = json.loads(request.content)
            if request.url.host == 'api.groq.com':
                self.assertEqual(request.headers['authorization'], 'Bearer groq-test-key')
                self.assertEqual(payload['response_format'], {'type': 'json_object'})
                return httpx.Response(200, json={'choices': [{'message': {'content': '{"ok":true}'}}]})
            self.assertEqual(request.url.host, 'api.jina.ai')
            self.assertEqual(request.headers['authorization'], 'Bearer jina-test-key')
            self.assertEqual(payload['task'], 'retrieval.passage')
            self.assertEqual(payload['dimensions'], 2048)
            vector = b64encode(pack('<f', 0.5) * 2048).decode()
            return httpx.Response(200, json={'data': [{'embedding': vector}]})

        result = check_groq_jina(SETTINGS, transport=httpx.MockTransport(respond))
        self.assertEqual(result['groq']['status'], 'OK')
        self.assertEqual(result['jina']['dimensions'], 2048)

    def test_provider_responses_with_errors_are_never_echoed(self):
        def respond(request):
            if request.url.host == 'api.groq.com':
                return httpx.Response(429, text=SETTINGS['GROQ_API_KEY'])
            return httpx.Response(200, json={'data': [{'embedding': 'AAAAAA=='}]})

        result = check_groq_jina(SETTINGS, transport=httpx.MockTransport(respond))
        self.assertEqual(result['groq'], {'status': 'RATE_LIMITED', 'http_status': 429})
        self.assertEqual(result['jina']['status'], 'INVALID_EMBEDDING')
        self.assertNotIn(SETTINGS['GROQ_API_KEY'], json.dumps(result))

    def test_failed_index_maps_only_recognized_statuses(self):
        for message, expected in [
            ('Error code: 429 - private provider body', 'INDEX_PROVIDER_RATE_LIMITED'),
            ('RetryError[Future raised RateLimitError]', 'INDEX_PROVIDER_RATE_LIMITED'),
            ('AUTHZ_INSUFFICIENT_BALANCE', 'INDEX_PROVIDER_ACCESS_DENIED'),
            ('503 SERVICE_UNAVAILABLE', 'INDEX_PROVIDER_UNAVAILABLE'),
            ('unrecognized failure', 'INDEX_FAILED'),
        ]:
            with self.subTest(code=expected):
                self.assertEqual(_index_failure_code([{'status': 'failed', 'error_msg': message}]), expected)


    def test_packed_sources_preserve_quotes_and_all_locators(self):
        documents = [
            dict(document_id='v1', role='BASE', filename='v1.docx', file_type='DOCX',
                 blocks=[dict(source_ref='block:1', text='Điều 1.'), dict(source_ref='block:2', text='30 ngày.'),
                         dict(source_ref='block:4', text='Điều 2.')]),
            dict(document_id='s', role='AMENDMENT', filename='s.docx', file_type='DOCX',
                 blocks=[dict(source_ref='block:5', text='15 ngày.')]),
        ]
        blocks = build_chunks('comparison', documents, {'v1': 'v1', 's': 's'})
        packed = pack_adjacent_chunks(blocks, 100)
        self.assertEqual([c.source_refs for c in packed],
                         [('block:1', 'block:2'), ('block:4',), ('block:5',)])
        registry = SourceRegistry(packed, documents)
        evidence = registry.evidence(dict(file_path=packed[0].file_source, content=packed[0].indexed_text))
        self.assertEqual(evidence['quote'], chr(10).join(('Điều 1.', '30 ngày.')))
        self.assertEqual(evidence['source_refs'], ['block:1', 'block:2'])
        self.assertEqual(pack_adjacent_chunks(blocks, 8), blocks)
