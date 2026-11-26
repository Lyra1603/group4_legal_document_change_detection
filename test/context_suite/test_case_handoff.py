"""Contract, source identity and owned-resource tests; NO provider calls here."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

import httpx

from backend.app.config import LightRAGConfig
from backend.app.context.case_handoff import ContextCase
from backend.app.context.source_registry import SourceRegistry
from backend.app.context.case_runner import run_case, audit_extracted_graph
from backend.app.context.lightrag_client import LightRAGClient, RetrievalError
from backend.app.context.owned_server import OwnedLightRAG, read_provider_env
from test.context_suite.support import ContractServer

ROOT=Path(__file__).resolve().parents[2]


class CaseHandoffTests(unittest.TestCase):
    def setUp(self):
        self.raw=json.loads((ROOT/'test/fixtures/context_cases/synthetic_civil.json').read_text(encoding='utf-8'))
        self.case=ContextCase.from_dict(self.raw)
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def run_case(self,behavior='normal',session='comparison-a',*,diff=None,repeats=1):
        registry=self.case.registry(session)
        server=ContractServer(behavior=behavior)
        client=LightRAGClient(LightRAGConfig('http://contract-double:9621','demo',poll_interval=.001),
                             session,Path(self.temp.name)/session,deadline=time.monotonic()+2,
                             transport=httpx.MockTransport(server))
        try:
            result=run_case(self.case,client,registry,text_diff=diff,repeats=repeats)
            return result,server
        finally:
            client.cleanup(budget=.03)

    def test_real_shape_keeps_source_identity_and_does_not_change_input(self):
        before=deepcopy(self.raw)
        result,server=self.run_case(repeats=2)
        self.assertTrue(result['retrieval_completed'])
        self.assertEqual(self.raw,before)
        self.assertTrue(result['enabled']['repeat_consistent'])
        self.assertEqual(len(server.queries),3)
        query=json.loads(server.queries[0])
        self.assertEqual(query['text_diff'],result['text_diff'])
        self.assertTrue(result['enabled']['source_trace'])
        for trace in result['enabled']['source_trace']:
            self.assertEqual(trace['version_id'],'fixture-v1')
            self.assertTrue(trace['unit_paths'])
            self.assertTrue(trace['evidence']['source_refs'])
        self.assertFalse(result['semantic_executed'])
        self.assertFalse(result['candidate_retrieval']['legal_impact_confirmed'])
        self.assertEqual(result['candidate_retrieval']['status'],'CANDIDATES_ONLY')
        # Retrieval does not silently resolve ReferenceRequirement or legal review.
        refs=result['enabled']['amendment']['context']['references']
        self.assertEqual(refs,self.case.amendment['context']['references'])
        self.assertTrue(result['enabled']['amendment']['needs_review'])

    def test_same_filename_does_not_merge_source_nodes(self):
        registry=self.case.registry('comparison-a')
        self.assertEqual(len({d['filename'] for d in self.case.documents}),1)
        graph=registry.source_graph()
        self.assertEqual(len([n for n in graph['nodes'] if n['type']=='DocumentVersion']),3)
        result,_=self.run_case()
        self.assertEqual({x['source_identity'] for x in result['enabled']['source_trace']},
                         {'synthetic:v1','synthetic:s','synthetic:ref_1'})

    def test_later_retrieval_failure_cannot_be_reported_as_full_success(self):
        delegate=ContractServer();calls=[0]
        def alternating(request):
            if request.url.path=='/query/data':
                calls[0]+=1
                delegate.behavior='foreign' if calls[0]==2 else 'normal'
            return delegate(request)
        registry=self.case.registry('repeated')
        client=LightRAGClient(LightRAGConfig('http://contract-double:9621','demo'),
            'repeated',Path(self.temp.name)/'repeated',deadline=time.monotonic()+10,
            transport=httpx.MockTransport(alternating))
        try:
            result=run_case(self.case,client,registry,repeats=2)
            self.assertFalse(result['retrieval_completed'])
            self.assertEqual([q['verified'] for q in result['enabled']['query_samples']],[True,False])
            self.assertEqual(result['enabled']['issues'][0]['code'],'RETRIEVAL_SOURCE_REJECTED')
            self.assertFalse(result['enabled']['repeat_consistent'])
        finally:client.cleanup()

    def test_subset_registry_is_rejected_before_ingestion(self):
        full=self.case.registry('subset')
        registry=SourceRegistry(list(full.chunks.values())[:2],self.case.documents)
        server=ContractServer()
        client=LightRAGClient(LightRAGConfig('http://contract-double:9621','demo'),
            'subset',Path(self.temp.name)/'subset',deadline=time.monotonic()+10,
            transport=httpx.MockTransport(server))
        try:
            with self.assertRaisesRegex(ValueError,'source blocks'):run_case(self.case,client,registry)
            self.assertEqual(server.calls,[])
        finally:client.close()

    def test_draft_envelope_keeps_legacy_report_and_sources_valid(self):
        from backend.app.schemas.report_validation import validate_report,validate_sources
        draft=json.loads((ROOT/'test/fixtures/context_cases/analysis_report_draft.json').read_text(encoding='utf-8'))
        self.assertEqual(draft['proposal_version'],'DRAFT-2026-11-22')
        report=draft['report']['targets'][0]['report']
        validate_report(report)
        validate_sources(report,{d['document_id']:d for d in self.case.documents})
        self.assertEqual(set(draft['report']['targets'][0]['source_bindings']),
                         {d['document_id'] for d in self.case.documents})
        self.assertEqual(draft['report']['coverage']['indirect_analysis'],'NOT_RUN')

    def test_changed_text_rejects_stale_provenance_digest(self):
        self.raw['documents'][0]['blocks'][0]['text']+=' changed'
        with self.assertRaisesRegex(ValueError,'digest'):
            ContextCase.from_dict(self.raw)

    def test_missing_or_ambiguous_version_rejected(self):
        for value in ['',None]:
            raw=deepcopy(self.raw);raw['provenance']['v1']['version_id']=value
            with self.assertRaises(ValueError):ContextCase.from_dict(raw)
        raw=deepcopy(self.raw);raw['provenance']['s'].update(source_identity='synthetic:v1',version_id='fixture-v1')
        with self.assertRaisesRegex(ValueError,'Ambiguous'):ContextCase.from_dict(raw)

    def test_dataset_input_requires_namespaced_id_and_immutable_revision(self):
        raw=deepcopy(self.raw);raw['source_kind']='DATASET_UNREVIEWED'
        with self.assertRaises(ValueError):ContextCase.from_dict(raw)
        for m in raw['provenance'].values():
            m.update(dataset='th1nhng0/vietnamese-legal-documents',dataset_id=m['source_identity'],
                     revision='a'*40,source_url='https://example.org/source')
        self.assertEqual(ContextCase.from_dict(raw).source_kind,'DATASET_UNREVIEWED')
        raw['provenance']['v1']['revision']='main'
        with self.assertRaises(ValueError):ContextCase.from_dict(raw)

    def test_uploaded_s_can_mix_with_pinned_dataset_v1(self):
        raw=deepcopy(self.raw);raw['source_kind']='DATASET_UNREVIEWED'
        raw['provenance']['s']['origin']='UPLOAD'
        for did in ['v1','ref_1']:
            raw['provenance'][did].update(dataset='th1nhng0/vietnamese-legal-documents',
                dataset_id=did,revision='a'*40,source_url='https://example.org/source')
        self.assertEqual(ContextCase.from_dict(raw).source_kind,'DATASET_UNREVIEWED')

    def test_duplicate_local_document_id_rejected(self):
        self.raw['documents'].append(deepcopy(self.raw['documents'][0]))
        with self.assertRaises(ValueError):ContextCase.from_dict(self.raw)

    def test_missing_block_location_rejected(self):
        self.raw['provenance']['v1']['unit_paths']={}
        with self.assertRaises(ValueError):ContextCase.from_dict(self.raw)

    def test_no_v1_never_fabricates_context_case(self):
        self.raw['amendment']['before_text']=None
        with self.assertRaises(ValueError):ContextCase.from_dict(self.raw)

    def test_source_scope_and_literal_quote_required(self):
        for evidence in [dict(document_id='unknown',source_refs=['block:1'],quote='bad'),
                         dict(document_id='v1',source_refs=['block:99'],quote='bad')]:
            raw=deepcopy(self.raw);raw['amendment']['evidence'].append(evidence)
            with self.assertRaises(ValueError):ContextCase.from_dict(raw)

    def test_forged_quoted_after_rejected(self):
        self.raw['amendment']['after_basis']='QUOTED'
        with self.assertRaisesRegex(ValueError,'Quoted'):ContextCase.from_dict(self.raw)

    def test_foreign_or_paraphrased_batch_never_partially_enters_context(self):
        for behavior in ['foreign','paraphrase']:
            result,_=self.run_case(behavior,session=behavior)
            self.assertFalse(result['retrieval_completed'])
            self.assertEqual(result['enabled']['issues'][0]['code'],'RETRIEVAL_SOURCE_REJECTED')
            self.assertEqual(result['enabled']['amendment']['context'],self.case.amendment['context'])
            self.assertEqual(result['candidate_retrieval']['evidence'],[])

    def test_empty_and_timeout_preserve_uncertainty(self):
        for behavior,code in [('empty','RETRIEVAL_EMPTY_UNCONFIRMED'),('timeout','RETRIEVAL_TIMEOUT')]:
            result,_=self.run_case(behavior,session=behavior)
            self.assertFalse(result['retrieval_completed'])
            self.assertEqual(result['enabled']['issues'][0]['code'],code)
            self.assertEqual(result['enabled']['amendment']['context'],self.case.amendment['context'])
            self.assertFalse(result['candidate_retrieval']['legal_impact_confirmed'])

    def test_no_client_never_claims_retrieval_success(self):
        with self.assertRaisesRegex(ValueError,'explicit retrieval client'):
            run_case(self.case,None,self.case.registry('none'))

    def test_registry_from_other_comparison_or_version_rejected_before_http(self):
        registry=self.case.registry('foreign-session')
        server=ContractServer()
        client=LightRAGClient(LightRAGConfig('http://contract-double:9621','demo'),
                             'local-session',Path(self.temp.name)/'local-session',deadline=time.monotonic()+10,
                             transport=httpx.MockTransport(server))
        try:
            with self.assertRaisesRegex(ValueError,'mismatch'):run_case(self.case,client,registry)
            registry=self.case.registry('local-session')
            self.case.provenance['v1']['version_id']='other-version'
            with self.assertRaisesRegex(ValueError,'mismatch'):run_case(self.case,client,registry)
            self.assertFalse(server.calls)
        finally:client.close()

    def test_wrong_diff_stops_before_index_or_query(self):
        from backend.app.change_analysis.text_diff import compute_text_diff
        diff=compute_text_diff(self.case.amendment);diff['amendment_id']='other'
        with self.assertRaisesRegex(ValueError,'ID mismatch'):self.run_case(diff=diff)

    def test_two_parallel_comparisons_reject_each_others_sources(self):
        with ThreadPoolExecutor(2) as pool:
            a,b=list(pool.map(lambda sid:self.run_case(session=sid),['parallel-a','parallel-b']))
        self.assertTrue(a[0]['retrieval_completed']);self.assertTrue(b[0]['retrieval_completed'])
        registry=self.case.registry('parallel-a')
        for chunk in b[0]['enabled']['raw_retrieval']['chunks']:
            with self.assertRaises(ValueError):registry.evidence(chunk)

    def test_read_only_query_retries_once_after_transient_error(self):
        delegate=ContractServer();count=[0]
        def flaky(request):
            if request.url.path=='/query/data':
                count[0]+=1
                if count[0]==1:return httpx.Response(500,json={'detail':'provider unavailable'})
            return delegate(request)
        registry=self.case.registry('flaky')
        client=LightRAGClient(LightRAGConfig('http://contract-double:9621','demo'),
                             'flaky',Path(self.temp.name)/'flaky',deadline=time.monotonic()+10,
                             transport=httpx.MockTransport(flaky))
        try:
            result=run_case(self.case,client,registry)
            self.assertTrue(result['retrieval_completed'])
            self.assertEqual(count[0],3) # retry once + candidate query
        finally:client.cleanup()

    def test_graph_flags_merged_units_without_promoting_legal_relations(self):
        registry=self.case.registry('graph')
        sources=list(registry.chunks)
        graph={'nodes':[{'id':'Điều 1','properties':{'file_path':'<SEP>'.join(sources[:2])}},
                        {'id':'unknown','properties':{'file_path':'foreign.txt'}}],'edges':[]}
        audit=audit_extracted_graph(graph,registry)
        self.assertEqual(audit['possible_cross_document_unit_merges'][0]['document_ids'],['s','v1'])
        self.assertEqual(len(audit['unknown_sources']),1)
        self.assertFalse(audit['legal_relations_verified'])

    def test_malformed_graph_is_explicit_protocol_failure(self):
        for graph in [{'nodes':None},{'nodes':[None]},
                      {'nodes':[{'id':'x','properties':{'file_path':99}}]}]:
            with self.subTest(graph=graph),self.assertRaises(ValueError):
                audit_extracted_graph(graph,self.case.registry('graph-error'))

    def test_oversize_block_fails_instead_of_truncating(self):
        with self.assertRaisesRegex(ValueError,'bound'):self.case.registry('x',max_chars=1)


class OwnedServerTests(unittest.TestCase):
    def test_refuses_existing_session_directory(self):
        with tempfile.TemporaryDirectory() as root:
            OwnedLightRAG(root,'a'*32,{})
            with self.assertRaises(FileExistsError):OwnedLightRAG(root,'a'*32,{})

    def test_no_credentials_does_not_create_container_or_secret_file(self):
        with tempfile.TemporaryDirectory() as root,patch('backend.app.context.owned_server.docker') as docker:
            service=OwnedLightRAG(root,'b'*32,{})
            with self.assertRaises(RetrievalError):service.start()
            docker.assert_not_called()
            self.assertFalse((service.directory/'.env').exists())
            self.assertEqual(service.finish(),[])

    def test_mismatched_owner_never_stops_or_removes_server(self):
        with tempfile.TemporaryDirectory() as root,patch('backend.app.context.owned_server.docker',return_value='foreign') as docker:
            service=OwnedLightRAG(root,'c'*32,{})
            service.started=True
            self.assertEqual(service.finish(),['CLEANUP_SCOPE_MISMATCH'])
            self.assertEqual(docker.call_count,1)
            self.assertEqual(docker.call_args.args[0][0],'inspect')

    def test_cleanup_only_targets_owned_container(self):
        with tempfile.TemporaryDirectory() as root,patch('backend.app.context.owned_server.docker',return_value='d'*32) as docker:
            service=OwnedLightRAG(root,'d'*32,{})
            service.started=True
            self.assertEqual(service.finish(),[])
            self.assertEqual([c.args[0][0] for c in docker.call_args_list],['inspect','stop','rm'])
            self.assertTrue(all(service.name in c.args[0] for c in docker.call_args_list))

    def test_owned_container_is_stopped_even_if_http_cleanup_crashes(self):
        from unittest.mock import Mock
        with tempfile.TemporaryDirectory() as root,patch('backend.app.context.owned_server.docker',return_value='e'*32) as docker:
            service=OwnedLightRAG(root,'e'*32,{})
            service.started=True
            service.client=Mock()
            service.client.cleanup.side_effect=ValueError('protocol failure')
            self.assertEqual(service.finish(),['CLEANUP_PENDING'])
            self.assertEqual([c.args[0][0] for c in docker.call_args_list],['inspect','stop','rm'])
            service.client.close.assert_called_once()

    def test_lost_docker_run_ack_still_cleans_exact_owned_container(self):
        settings={'LEGAL_AI_PROVIDER':'gemini','GEMINI_API_KEY':'test-only-not-a-secret',
                  'GEMINI_MODEL':'test-model','GEMINI_EMBEDDING_MODEL':'test-embedding','GEMINI_EMBEDDING_DIM':'3'}
        with tempfile.TemporaryDirectory() as root:
            service=OwnedLightRAG(root,'f'*32,settings)
            def daemon(args,**kwargs):
                if args[0]=='image':return 'sha256:resolved-image'
                if args[0]=='run':raise RetrievalError('DOCKER_UNAVAILABLE')
                if args[0]=='ps':return service.name
                if args[0]=='inspect':return service.session_id
                return ''
            with patch('backend.app.context.owned_server.docker',side_effect=daemon) as docker:
                with self.assertRaises(RetrievalError):service.start()
                self.assertTrue(service.launch_attempted)
                self.assertFalse(service.started)
                self.assertFalse((service.directory/'.env').exists())
                self.assertEqual(service.finish(),[])
                run_args=next(c.args[0] for c in docker.call_args_list if c.args[0][0]=='run')
                self.assertEqual(run_args[-1],'sha256:resolved-image')
                self.assertEqual([c.args[0][0] for c in docker.call_args_list][-4:],['ps','inspect','stop','rm'])

    def test_lost_ack_does_not_delete_a_foreign_container(self):
        with tempfile.TemporaryDirectory() as root:
            service=OwnedLightRAG(root,'a'*32,{})
            service.launch_attempted=True
            with patch('backend.app.context.owned_server.docker',side_effect=[service.name,'foreign']) as docker:
                self.assertEqual(service.finish(),['CLEANUP_SCOPE_MISMATCH'])
                self.assertEqual([c.args[0][0] for c in docker.call_args_list],['ps','inspect'])

    def test_no_container_created_after_failed_launch_requires_no_deletion(self):
        with tempfile.TemporaryDirectory() as root:
            service=OwnedLightRAG(root,'a'*32,{})
            service.launch_attempted=True
            with patch('backend.app.context.owned_server.docker',return_value='') as docker:
                self.assertEqual(service.finish(),[])
                self.assertEqual(docker.call_args.args[0][0],'ps')

    def test_close_error_still_stops_owned_container(self):
        from unittest.mock import Mock
        with tempfile.TemporaryDirectory() as root,patch('backend.app.context.owned_server.docker',return_value='e'*32) as docker:
            service=OwnedLightRAG(root,'e'*32,{})
            service.started=True
            service.client=Mock()
            service.client.cleanup.return_value=None
            service.client.close.side_effect=ValueError('close failure')
            self.assertEqual(service.finish(),['CLEANUP_PENDING'])
            self.assertEqual([c.args[0][0] for c in docker.call_args_list],['inspect','stop','rm'])

    def test_env_reader_does_not_execute_shell_syntax(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/'provider.env';path.write_text('PRIVATE_TEST_VALUE=$(never_execute)\n',encoding='utf-8')
            self.assertEqual(read_provider_env(path)['PRIVATE_TEST_VALUE'],'$(never_execute)')


class CliReviewTests(unittest.TestCase):
    def test_invalid_repeat_count_fails_before_service_start(self):
        from backend.context_cli import main
        args=['context_cli','--input',str(ROOT/'test/fixtures/context_cases/synthetic_civil.json'),
              '--output','unused.json','--mode','real','--repeats','0']
        with patch('sys.argv',args),patch('backend.context_cli.OwnedLightRAG') as owner,patch('sys.stderr'):
            with self.assertRaises(SystemExit) as caught:main()
            self.assertEqual(caught.exception.code,2)
            owner.assert_not_called()

    def test_graph_protocol_error_is_not_mislabelled_as_cleanup_failure(self):
        from backend.context_cli import main
        with tempfile.TemporaryDirectory() as root:
            output=Path(root)/'report.json'
            args=['context_cli','--input',str(ROOT/'test/fixtures/context_cases/synthetic_civil.json'),
                  '--output',str(output),'--mode','real']
            with patch('sys.argv',args),patch('backend.context_cli.OwnedLightRAG') as owner, \
                 patch('backend.context_cli.read_provider_env',return_value={}), \
                 patch('backend.context_cli.run_case',return_value={'retrieval_completed':True}),patch('builtins.print'):
                owner.return_value.start.return_value.graph.return_value={'nodes':None}
                owner.return_value.profile={'provider':'test'}
                owner.return_value.image_id='test-image'
                owner.return_value.finish.return_value=[]
                self.assertEqual(main(),1)
            report=json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(report['graph_issues'],['GRAPH_PROTOCOL_ERROR'])
            self.assertEqual(report['cleanup_issues'],[])
            self.assertTrue(report['retrieval_completed'])


if __name__=='__main__':unittest.main()
