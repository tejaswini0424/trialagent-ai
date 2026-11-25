from types import SimpleNamespace
import pytest
from backend.orchestration.orchestrator import analyze,MODULES
from backend.database.db_operations import save_document,save_analysis,get_document,documents,history
from backend.authentication.auth import register
def test_pipeline(sample):
 states=[];out=analyze(sample,lambda *x:states.append(x));assert out['status']=='Completed';assert len(out['agents'])==7;assert len(states)==14;assert all(l['duration']>=0 for l in out['agents'])
def test_failure_isolation(sample):
 def fail(*args): raise RuntimeError('Injected failure')
 modules=[SimpleNamespace(run=fail)]+MODULES[1:];out=analyze(sample,modules=modules)
 assert out['agents'][0]['status']=='Failed';assert out['agents'][0]['attempts']==2;assert out['agents'][2]['status']=='Skipped';assert out['agents'][-1]['status']=='Completed';assert out['status']=='Partial'
def test_retry(sample):
 attempts=[]
 def flaky(doc,ctx):
  attempts.append(1)
  if len(attempts)==1: raise OSError('Temporary failure')
  return MODULES[0].run(doc,ctx)
 out=analyze(sample,modules=[SimpleNamespace(run=flaky)]+MODULES[1:]);assert out['agents'][0]['status']=='Completed';assert out['agents'][0]['attempts']==2
def test_ownership_and_duplicates(sample):
 a=register('alice','a','a');b=register('bob','b','b');did,dup=save_document(a,sample);assert not dup;assert save_document(a,sample)==(did,True)
 with pytest.raises(PermissionError): get_document(b,did)
 with pytest.raises(PermissionError): save_analysis(b,did,analyze(sample))
 assert documents(b)==[];save_analysis(a,did,analyze(sample));assert get_document(a,did).status=='Completed';assert len(history(a))==1
