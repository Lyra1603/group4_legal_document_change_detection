"""Disposable Docker instance for one Context demo, never a shared-corpus client.

Reuses the existing upstream image, HTTP adapter and targeted-ID cleanup. No
model credentials are printed, persisted in reports or passed as CLI arguments.
"""
from pathlib import Path
import os
import re
import secrets
import subprocess
import time

from ..config import LightRAGConfig
from .lightrag_client import LightRAGClient, RetrievalError
from .provider_settings import groq_demo_options, provider_environment

IMAGE = 'pocs-lightrag:28ff1b05'
LABEL = 'pocs.context.session'


def read_provider_env(path=None):
    values = dict(os.environ)
    if path is not None:
        for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
            line=line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                raise ValueError('Expected KEY=VALUE provider configuration')
            key,value=line.split('=',1)
            if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',key):
                raise ValueError('Invalid environment key')
            if len(value)>=2 and value[0]==value[-1] and value[0] in {'"',"'"}:
                value=value[1:-1]
            values[key]=value
    return values


def docker(args, timeout=60):
    try:
        result=subprocess.run(['docker',*args],capture_output=True,timeout=timeout,
                              creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    except (OSError,subprocess.TimeoutExpired):
        raise RetrievalError('DOCKER_UNAVAILABLE') from None
    if result.returncode:
        # Docker error bodies may include environment or provider configuration.
        raise RetrievalError('DOCKER_COMMAND_FAILED')
    return result.stdout.decode('utf-8',errors='replace').strip()


class OwnedLightRAG:
    def __init__(self, directory, session_id, settings, *, budget=600):
        if not re.fullmatch('[0-9a-f]{32}',session_id):
            raise ValueError('Use a fresh UUID session')
        if not 30 <= budget <= 1800:
            raise ValueError('Session budget must be 30..1800 seconds')
        self.session_id=session_id
        self.comparison_id=session_id
        self.directory=Path(directory).resolve()/session_id
        # A new instance must never attach to an existing directory/ledger.
        self.directory.mkdir(parents=True,exist_ok=False)
        self.settings=settings
        self.deadline=time.monotonic()+budget
        self.name='pocs-context-'+session_id
        self.started=False
        self.launch_attempted=False
        self.client=None
        self.image_id=None

    def start(self):
        settings=self.settings
        provider = settings.get('LEGAL_AI_PROVIDER', 'gemini')
        provider_env = provider_environment(settings)
        mixed = provider == 'groq-jina'
        server_key=secrets.token_urlsafe(32)
        workspace='context_'+self.session_id
        self.image_id=docker(['image','inspect',IMAGE,'--format','{{.Id}}'])
        env={'HOST':'0.0.0.0','PORT':'9621','WORKSPACE':workspace,
             'LIGHTRAG_API_KEY':server_key, **provider_env,
             'WORKING_DIR':'/app/data/rag_storage','INPUT_DIR':'/app/data/inputs',
             'PROMPT_DIR':'/app/data/prompts','LOG_DIR':'/app/data/logs',
             'SUMMARY_LANGUAGE':'Vietnamese','MAX_ASYNC_LLM':'1','EXTRACT_MAX_ASYNC_LLM':'1',
             'KEYWORD_MAX_ASYNC_LLM':'1','EMBEDDING_FUNC_MAX_ASYNC':'1','MAX_PARALLEL_INSERT':'1',
             'CHUNK_SIZE':'3000','CHUNK_OVERLAP_SIZE':'0','LOG_LEVEL':'WARNING',
             'LLM_TIMEOUT':'180','EMBEDDING_TIMEOUT':'180',
             'LIGHTRAG_KV_STORAGE':'JsonKVStorage','LIGHTRAG_DOC_STATUS_STORAGE':'JsonDocStatusStorage',
             'LIGHTRAG_GRAPH_STORAGE':'NetworkXStorage','LIGHTRAG_VECTOR_STORAGE':'NanoVectorDBStorage'}
        if mixed:
            env.update(groq_demo_options(env['LLM_MODEL']))
        if any('\n' in str(v) or '\r' in str(v) for v in env.values()):
            raise ValueError('Multiline environment value rejected')
        self.profile = {
            'provider': provider, 'model': env['LLM_MODEL'],
            'embedding_provider': 'jina' if mixed else provider,
            'embedding_model': env['EMBEDDING_MODEL'],
            'embedding_dim': int(env['EMBEDDING_DIM']),
        }
        env_file=self.directory/'.env'
        storage=self.directory/'data'
        storage.mkdir()
        with os.fdopen(os.open(env_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w', encoding='utf-8') as stream:
            stream.write('\n'.join(f'{k}={v}' for k,v in env.items())+'\n')
        try:
            self.launch_attempted=True
            docker(['run','--detach','--name',self.name,'--label',LABEL+'='+self.session_id,
                    '--publish','127.0.0.1::9621','--env-file',str(env_file),
                    '--mount',f'type=bind,source={storage},target=/app/data',self.image_id])
            self.started=True
        finally:
            # Only this generated credential file is removed; caller files stay intact.
            env_file.unlink(missing_ok=True)
        address=docker(['port',self.name,'9621/tcp'])
        if not re.fullmatch(r'127\.0\.0\.1:\d+',address):
            raise RetrievalError('SERVER_PORT_UNVERIFIED')
        config=LightRAGConfig('http://'+address,workspace,api_key=server_key,
                              timeout=180, top_k=8, max_tokens=3000 if mixed else 6000,
                              max_chunks=12 if mixed else 30, max_chunk_chars=2500 if mixed else 5000)
        self.client=LightRAGClient(config,self.comparison_id,self.directory/'leases',deadline=self.deadline)
        startup=min(self.deadline,time.monotonic()+90)
        while time.monotonic()<startup:
            try:
                self.client.verify_server()
                return self.client
            except RetrievalError as exc:
                if exc.code not in {'RETRIEVAL_UNAVAILABLE','RETRIEVAL_HTTP_ERROR','RETRIEVAL_TIMEOUT'}:
                    raise
            time.sleep(1)
        raise RetrievalError('LIGHTRAG_STARTUP_TIMEOUT')

    def finish(self):
        issues=[]
        if self.client:
            try:
                code=self.client.cleanup(budget=30)
                if code: issues.append(code)
            except Exception:
                # Still stop our owned server when an unexpected protocol/storage
                # error occurs. Never log exception bodies containing credentials.
                issues.append('CLEANUP_PENDING')
            finally:
                try:
                    self.client.close()
                except Exception:
                    if 'CLEANUP_PENDING' not in issues:
                        issues.append('CLEANUP_PENDING')
        if self.started or self.launch_attempted:
            try:
                if not self.started:
                    # docker run may have created the container before losing ACK.
                    names=docker(['ps','--all','--filter','name=^/'+self.name+'$', '--format','{{.Names}}'])
                    if not names:
                        self.launch_attempted=False
                        return issues
                    if names != self.name:
                        raise RetrievalError('CLEANUP_SCOPE_MISMATCH')
                owner=docker(['inspect',self.name,'--format','{{index .Config.Labels "'+LABEL+'"}}'])
                if owner!=self.session_id:
                    raise RetrievalError('CLEANUP_SCOPE_MISMATCH')
                docker(['stop','--time','10',self.name],timeout=30)
                docker(['rm',self.name],timeout=30)
                self.started=False
                self.launch_attempted=False
            except RetrievalError as exc:
                issues.append(exc.code)
        return issues
