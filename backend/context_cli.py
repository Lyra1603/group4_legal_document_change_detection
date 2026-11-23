"""Source-traced Context demo. Real mode always uses its own Docker instance."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import uuid
import time

import httpx

from .app.config import LightRAGConfig
from .app.context.case_handoff import ContextCase
from .app.context.case_runner import run_case, audit_extracted_graph
from .app.context.lightrag_client import LightRAGClient, RetrievalError
from .app.context.owned_server import OwnedLightRAG, read_provider_env


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--mode',choices=['contract','real'],default='contract')
    parser.add_argument('--provider-env-file',type=Path)
    parser.add_argument('--runtime-dir',type=Path,default=Path('runtime/lightrag/context-sessions'))
    parser.add_argument('--repeats',type=int,choices=range(1,4),default=1)
    parser.add_argument('--budget',type=int,default=600)
    args=parser.parse_args()
    if not 30 <= args.budget <= 1800:
        parser.error('--budget must be between 30 and 1800 seconds')
    # Validate input before starting a service or sending any source outside.
    case=ContextCase.from_dict(json.loads(args.input.read_text(encoding='utf-8-sig')))
    session_id=uuid.uuid4().hex
    registry=case.registry(session_id,max_chunks=30,max_chars=5000)
    result={'case_id':case.case_id,'source_kind':case.source_kind,'retrieval_completed':False}
    issues=[];graph_issues=[];failure=None;server=None;client=None
    mode='REAL_LIGHTRAG_HTTP' if args.mode=='real' else 'CONTRACT_DOUBLE_NOT_LIGHTRAG'
    with tempfile.TemporaryDirectory(prefix='pocs_context_contract_') as temporary:
        try:
            if args.mode=='real':
                server=OwnedLightRAG(args.runtime_dir,session_id,read_provider_env(args.provider_env_file),budget=args.budget)
                client=server.start()
            else:
                # The test double is never a fallback for real mode.
                from test.context_suite.support import ContractServer
                client=LightRAGClient(LightRAGConfig('http://contract-double:9621','demo'),
                    session_id,Path(temporary),deadline=time.monotonic()+30,
                    transport=httpx.MockTransport(ContractServer()))
            result=run_case(case,client,registry,repeats=args.repeats)
            if args.mode=='real':
                try:
                    result['upstream_extracted_graph']=client.graph()
                    result['graph_source_audit']=audit_extracted_graph(result['upstream_extracted_graph'],registry)
                except RetrievalError as exc:
                    graph_issues.append(exc.code)
                except ValueError:
                    graph_issues.append('GRAPH_PROTOCOL_ERROR')
                result['provider']=server.profile
                result['image_id']=server.image_id
        except RetrievalError as exc:
            failure=exc.code
        finally:
            if server:
                issues.extend(server.finish())
            elif client:
                code=client.cleanup()
                if code:issues.append(code)
    result.update(mode=mode,generated_at=datetime.now(timezone.utc).isoformat(),failure=failure,
                  cleanup_issues=issues,graph_issues=graph_issues,comparison_id=session_id)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(args.output),'mode':mode,'source_kind':case.source_kind,
                      'retrieval_completed':result['retrieval_completed'],'failure':failure,
                      'cleanup_issues':issues, 'graph_issues':graph_issues, 'candidate_status':result.get('candidate_retrieval',{}).get('status') if result.get('candidate_retrieval') else None},ensure_ascii=True))
    candidate=result.get('candidate_retrieval')
    return 0 if result['retrieval_completed'] and not failure and not issues and not graph_issues and (not candidate or not candidate['issues']) else 1


if __name__=='__main__':
    raise SystemExit(main())
