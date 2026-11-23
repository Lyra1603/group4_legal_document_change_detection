"""Resolve the model and embedding provider independently of the web UI."""
from base64 import b64decode
from binascii import Error as Base64Error
import json
from math import isfinite
from struct import iter_unpack

import httpx

from .lightrag_client import RetrievalError

GROQ_URL = 'https://api.groq.com/openai/v1'
JINA_URL = 'https://api.jina.ai/v1/embeddings'


def provider_environment(settings):
    profile = settings.get('LEGAL_AI_PROVIDER', 'gemini')
    if profile == 'groq-jina':
        llm_binding, llm_host, llm_prefix = 'openai', GROQ_URL, 'GROQ'
        embed_binding, embed_host, embed_prefix = 'jina', JINA_URL, 'JINA'
    elif profile in ('gemini', 'openai'):
        host = ('https://generativelanguage.googleapis.com' if profile == 'gemini'
                else 'https://api.openai.com/v1')
        llm_binding = embed_binding = profile
        llm_host = embed_host = host
        llm_prefix = embed_prefix = profile.upper()
    else:
        raise RetrievalError('REAL_SERVICE_CONFIGURATION_REQUIRED')

    model = settings.get(llm_prefix + '_MODEL', '').strip()
    llm_key = settings.get(llm_prefix + '_API_KEY', '').strip()
    embedding = settings.get(embed_prefix + '_EMBEDDING_MODEL', '').strip()
    embedding_key = settings.get(embed_prefix + '_API_KEY', '').strip()
    dim = settings.get(embed_prefix + '_EMBEDDING_DIM', '').strip()
    values = (model, llm_key, embedding, embedding_key, dim)
    if not all(values) or not dim.isascii() or not dim.isdecimal() or len(dim) > 5 or int(dim) < 1:
        raise RetrievalError('REAL_SERVICE_CONFIGURATION_REQUIRED')
    if any('\n' in value or '\r' in value for value in values):
        raise RetrievalError('REAL_SERVICE_CONFIGURATION_REQUIRED')
    return {
        'LLM_BINDING': llm_binding, 'LLM_BINDING_HOST': llm_host,
        'LLM_MODEL': model, 'LLM_BINDING_API_KEY': llm_key,
        'EMBEDDING_BINDING': embed_binding, 'EMBEDDING_BINDING_HOST': embed_host,
        'EMBEDDING_MODEL': embedding, 'EMBEDDING_DIM': dim,
        'EMBEDDING_BINDING_API_KEY': embedding_key,
    }


def groq_demo_options(model):
    options = {
        'CHUNK_SIZE': '1000', 'MAX_GLEANING': '0',
        'OPENAI_LLM_MAX_COMPLETION_TOKENS': '1024',
        'EMBEDDING_ASYMMETRIC': 'true',
    }
    if model == 'qwen/qwen3.8-27b':
        options['OPENAI_LLM_REASONING_EFFORT'] = 'none'
    elif model in ('openai/gpt-oss-20b', 'openai/gpt-oss-120b'):
        options['OPENAI_LLM_REASONING_EFFORT'] = 'low'
    return options


def _probe(client, url, key, payload):
    try:
        response = client.post(url, headers={'Authorization': 'Bearer ' + key}, json=payload)
    except httpx.TimeoutException:
        return {'status': 'TIMEOUT'}, None
    except httpx.RequestError:
        return {'status': 'CONNECTION_FAILED'}, None
    if response.status_code != 200:
        status = {
            400: 'REQUEST_REJECTED', 401: 'KEY_REJECTED', 402: 'BALANCE_REQUIRED',
            403: 'ACCESS_OR_BALANCE_DENIED', 404: 'MODEL_OR_ENDPOINT_NOT_FOUND',
            429: 'RATE_LIMITED', 503: 'SERVICE_UNAVAILABLE',
        }.get(response.status_code, 'HTTP_ERROR')
        return {'status': status, 'http_status': response.status_code}, None
    try:
        return {'status': 'OK', 'http_status': 200}, response.json()
    except ValueError:
        return {'status': 'UNEXPECTED_RESPONSE', 'http_status': 200}, None


def check_groq_jina(settings, *, transport=None):
    """Send two small synthetic probes. Return safe diagnostics without provider bodies."""
    if settings.get('LEGAL_AI_PROVIDER') != 'groq-jina':
        raise RetrievalError('GROQ_JINA_PROFILE_REQUIRED')
    config = provider_environment(settings)
    prompt = 'Đây là phép thử. Trả JSON với trường ok có giá trị true.'
    llm_payload = dict(model=config['LLM_MODEL'], messages=[dict(role='user', content=prompt)],
                       response_format={'type': 'json_object'}, max_completion_tokens=128)
    effort = groq_demo_options(config['LLM_MODEL']).get('OPENAI_LLM_REASONING_EFFORT')
    if effort:
        llm_payload['reasoning_effort'] = effort
    dimension = int(config['EMBEDDING_DIM'])
    with httpx.Client(timeout=20, follow_redirects=False, trust_env=False, transport=transport) as client:
        groq, reply = _probe(client, GROQ_URL + '/chat/completions', config['LLM_BINDING_API_KEY'], llm_payload)
        if groq['status'] == 'OK':
            try:
                content = json.loads(reply['choices'][0]['message']['content'])
                if not isinstance(content, dict) or content.get('ok') is not True:
                    groq['status'] = 'UNEXPECTED_RESPONSE'
            except (ValueError, TypeError, KeyError, IndexError):
                groq['status'] = 'UNEXPECTED_RESPONSE'
        jina, reply = _probe(client, JINA_URL, config['EMBEDDING_BINDING_API_KEY'],
                             dict(model=config['EMBEDDING_MODEL'], input=['Một điều khoản mẫu.'],
                                  dimensions=dimension, task='retrieval.passage', embedding_type='base64'))
        if jina['status'] == 'OK':
            try:
                entries = reply['data']
                raw = b64decode(entries[0]['embedding'], validate=True)
                if len(entries) != 1 or len(raw) != 4 * dimension or not all(
                    isfinite(value) for (value,) in iter_unpack('<f', raw)
                ):
                    jina['status'] = 'INVALID_EMBEDDING'
                else:
                    jina['dimensions'] = dimension
            except (Base64Error, TypeError, ValueError, KeyError, IndexError):
                jina['status'] = 'INVALID_EMBEDDING'
    return {'groq': groq, 'jina': jina}
