import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

module_path=Path(__file__).with_name('civil_metadata_rules.py')
if not module_path.exists():
    module_path=Path(__file__).resolve().parents[2]/'data/legal-dataset-study/civil_metadata_rules.py'
spec=importlib.util.spec_from_file_location('civil_metadata_rules',module_path)
rules=importlib.util.module_from_spec(spec); spec.loader.exec_module(rules)


def row(identity='1',**values):
    return dict.fromkeys(rules.COLUMNS,'') | {'id':identity,'loai_van_ban':'Nghị định'} | values


class CivilMetadataRulesTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.metadata=self.root/'metadata.csv'; self.candidates=self.root/'ung_vien_dan_su.csv'

    def write(self,path,rows):
        with path.open('w',encoding='utf-8-sig',newline='') as handle:
            writer=csv.DictWriter(handle,fieldnames=rules.COLUMNS)
            writer.writeheader(); writer.writerows(rows)

    def read(self,path):
        with path.open(encoding='utf-8-sig',newline='') as handle: return list(csv.DictReader(handle))

    def test_new_topics_without_literal_dan_su(self):
        for title in ('Hướng dẫn lập di chúc','Đăng ký thế chấp tài sản','Quy định giao kết hợp đồng','Quyền hưởng dụng'):
            with self.subTest(title=title):
                result=rules.classify(row(title=title))
                self.assertFalse(result['phase1']); self.assertTrue(result['phase2'])

    def test_new_industry_and_agency_columns_change_weak_topic_decision(self):
        base=row(title='Hướng dẫn giải quyết tranh chấp')
        self.assertFalse(rules.classify(base)['phase2'])
        for context in ({'nganh':'Tư pháp'},{'co_quan_ban_hanh':'Tòa án nhân dân tối cao'}):
            result=rules.classify(base|context)
            self.assertTrue(result['phase2'])
            self.assertIn('R2_14_CONTEXT_COMBINATION',[h['rule_id'] for h in result['hits']])

    def test_general_industry_agency_or_type_alone_is_not_enough(self):
        result=rules.classify(row(title='Quản lý hoạt động chuyên môn',nganh='Tư pháp',co_quan_ban_hanh='Bộ Tư pháp',loai_van_ban='Luật'))
        self.assertFalse(result['phase1']); self.assertFalse(result['phase2'])

    def test_temporal_and_identity_fields_do_not_decide_domain(self):
        candidate=row(title='Quản lý hoạt động chuyên môn',so_ky_hieu='dân sự',nguoi_ky='Dân Sự',ngay_co_hieu_luc='dân sự',tinh_trang_hieu_luc='thừa kế')
        self.assertFalse(rules.classify(candidate)['phase2']); self.assertFalse(rules.classify(candidate)['phase1'])

    def test_personnel_is_not_dan_su(self):
        self.assertFalse(rules.classify(row(title='Quản lý nhân sự'))['phase1'])

    def test_collision_keeps_round1_but_flags_review(self):
        result=rules.classify(row(title='Quy định về kinh doanh sản phẩm mật mã dân sự'))
        self.assertTrue(result['phase1']); self.assertEqual(result['group'],'scope_conflict_review')
        self.assertIn('term_collision',result['flags'])

    def test_organization_and_related_subject_are_not_core_confirmations(self):
        result=rules.classify(row(title='Tuyển dụng công chức thi hành án dân sự'))
        self.assertEqual(result['group'],'mixed_context_review'); self.assertEqual(result['priority'],'low')

    def test_empty_title_can_use_topic_field(self):
        result=rules.classify(row(linh_vuc='Đăng ký giao dịch bảo đảm'))
        self.assertTrue(result['phase2'])
        evidence=[e for h in result['hits'] for e in h['evidence']]
        self.assertTrue(any(e['column']=='linh_vuc' for e in evidence))

    def test_application_information_is_used_only_if_present(self):
        self.assertFalse(rules.classify(row())['phase2'])
        self.assertTrue(rules.classify(row(thong_tin_ap_dung='Áp dụng với giao dịch bảo đảm'))['phase2'])

    def test_union_preserves_old_rows_values_and_metadata_bytes(self):
        old=row('UUID-a',title='Mật mã dân sự',tinh_trang_hieu_luc='Hết hiệu lực toàn bộ')
        new=row('0002',title='Hướng dẫn di chúc',ngay_het_hieu_luc='01/01/2000')
        irrelevant=row('3',title='Tuyển dụng công chức',nganh='Nội vụ')
        self.write(self.metadata,[old,new,irrelevant]); self.write(self.candidates,[old])
        before=self.metadata.read_bytes()
        report=rules.expand_candidates(self.metadata,self.candidates)
        self.assertEqual(self.read(self.candidates),[old,new])
        self.assertEqual(self.metadata.read_bytes(),before)
        self.assertEqual(report['summary']['added_this_run'],1)
        self.assertTrue(report['summary']['preserved_all_existing'])

    def test_repeated_run_is_idempotent_for_candidates_and_evidence(self):
        self.write(self.metadata,[row(title='Hướng dẫn di chúc')])
        rules.expand_candidates(self.metadata,self.candidates)
        evidence=self.root/'ung_vien_dan_su_luot2_evidence.csv'
        before=(self.candidates.read_bytes(),evidence.read_bytes())
        report=rules.expand_candidates(self.metadata,self.candidates)
        self.assertEqual(before,(self.candidates.read_bytes(),evidence.read_bytes()))
        self.assertEqual(report['summary']['added_this_run'],0)

    def test_dry_run_never_creates_outputs(self):
        self.write(self.metadata,[row(title='Di chúc')])
        result=rules.expand_candidates(self.metadata,self.candidates,dry_run=True)
        self.assertEqual(result['summary']['total_candidates'],1)
        self.assertEqual(sorted(p.name for p in self.root.iterdir()),['metadata.csv'])

    def test_aliasing_metadata_output_is_rejected(self):
        self.write(self.metadata,[row(title='Di chúc')]); before=self.metadata.read_bytes()
        with self.assertRaises(ValueError): rules.expand_candidates(self.metadata,self.metadata)
        self.assertEqual(before,self.metadata.read_bytes())

    def test_duplicate_ids_and_revision_mismatch_fail_before_writing(self):
        self.write(self.metadata,[row(),row()])
        with self.assertRaises(ValueError): rules.expand_candidates(self.metadata,self.candidates)
        self.assertFalse(self.candidates.exists())
        self.write(self.metadata,[row(title='Di chúc')]); self.write(self.candidates,[row(title='Khác nguồn')])
        before=self.candidates.read_bytes()
        with self.assertRaises(ValueError): rules.expand_candidates(self.metadata,self.candidates)
        self.assertEqual(before,self.candidates.read_bytes())

    def test_all_17_columns_have_explicit_policy_and_evidence_has_basis(self):
        self.assertEqual(set(rules.COLUMNS),set(rules.COLUMN_POLICY))
        self.write(self.metadata,[row(title='Di chúc')])
        report=rules.expand_candidates(self.metadata,self.candidates)
        self.assertEqual(len(report['column_policy']),17)
        self.assertEqual(report['column_policy']['thong_tin_ap_dung']['observed_nonempty'],0)
        evidence=self.read(self.root/'ung_vien_dan_su_luot2_evidence.csv')[0]
        for hit in json.loads(evidence['evidence_json']):
            self.assertIn(hit['basis'],report['sources'])
            self.assertEqual(hit['evidence'][0]['value'],'Di chúc')

    def test_related_family_and_ip_not_labeled_as_core(self):
        for title in ('Luật Hôn nhân và gia đình','Luật Sở hữu trí tuệ'):
            with self.subTest(title=title):
                self.assertEqual(rules.classify(row(title=title))['group'],'related_candidate')

    def test_generic_assurance_measures_are_not_civil_security(self):
        result=rules.classify(row(title='Quy định các biện pháp bảo đảm thực hiện dân chủ ở cơ sở',nganh='Nội vụ'))
        self.assertFalse(result['phase1']); self.assertFalse(result['phase2'])

    def test_public_property_context_is_retained_but_not_high_priority(self):
        result=rules.classify(row(title='Phân cấp thẩm quyền xác lập quyền sở hữu toàn dân về tài sản'))
        self.assertTrue(result['phase2'])
        self.assertEqual(result['group'],'mixed_context_review'); self.assertEqual(result['priority'],'low')

    def test_missing_metadata_is_not_interpreted_as_exclusion(self):
        self.write(self.metadata,[row()])
        result=rules.expand_candidates(self.metadata,self.candidates)
        self.assertEqual(result['summary']['total_candidates'],0)
        self.assertTrue(result['summary']['not_selected_is_not_legal_exclusion'])

    def test_concurrent_candidate_edit_is_not_overwritten(self):
        first=row('1',title='Di chúc'); second=row('2',title='Quyền nhân thân')
        self.write(self.metadata,[first,second]); self.write(self.candidates,[first])
        original_classify=rules.classify
        def change_during_scan(value):
            self.write(self.candidates,[first,second])
            return original_classify(value)
        with patch.object(rules,'classify',side_effect=change_during_scan):
            with self.assertRaisesRegex(RuntimeError,'thay đổi'):
                rules.expand_candidates(self.metadata,self.candidates)
        self.assertEqual(self.read(self.candidates),[first,second])


if __name__=='__main__': unittest.main()
