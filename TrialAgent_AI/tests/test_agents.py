from backend.orchestration.orchestrator import analyze
from config.regulatory_checklist import load_checklist
def test_extraction(sample):
 out=analyze(sample);p=out['results']['Protocol Extraction']['protocol'];assert 'TEAL-01' in p['title'];assert p['inclusion_criteria'];assert p['dosage']
def test_design_eligibility_safety(sample):
 results=analyze(sample)['results'];assert 'Randomized' in results['Study Design']['details']['allocation'];assert any('Duplicate' in f['title'] for f in results['Eligibility']['findings']);assert any(f['severity']=='High' for f in results['Safety Review']['findings'])
def test_checklist(sample):
 result=analyze(sample)['results']['Regulatory Review'];assert len(result['findings'])==12;assert result['checklist']['version']=='1.0';assert all(f['reference_version'] for f in result['findings'])
def test_consistency(sample):
 fs=analyze(sample)['results']['Consistency']['findings'];titles=' '.join(f['title'] for f in fs);assert 'enrollment' in titles;assert 'precedes' in titles;assert 'endpoint' in titles;assert 'Cross-reference' in titles

def test_evidence_grounded(sample):
 for f in analyze(sample)['findings']:
  if f['page'] is not None: assert f['page'] in [p['number'] for p in sample['pages']]

def test_negative_evidence_not_present():
 from backend.document_processing.document_loader import load_document
 from backend.agents.regulatory_review_agent import run
 doc=load_document('negative.txt',b'Ethics committee approval not provided.')
 results=run(doc,{})
 assert next(f for f in results['findings'] if f['checklist_id']=='RG-12')['status']=='Missing'
def test_not_applicable(sample):
 from backend.agents.regulatory_review_agent import run
 checklist=load_checklist();checklist['items'][0]['not_applicable']=True
 assert run(sample,{'_checklist':checklist})['findings'][0]['status']=='Not Applicable'
