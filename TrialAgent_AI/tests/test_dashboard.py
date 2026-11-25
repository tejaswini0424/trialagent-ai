from pathlib import Path
from streamlit.testing.v1 import AppTest
def test_auth_screen():
 at=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py')).run(timeout=30)
 assert not at.exception;assert any(b.label=='Login' for b in at.button);assert any(b.label=='Create Account' for b in at.button)
def test_all_authenticated_pages(sample):
 from backend.authentication.auth import register
 from backend.database.db_operations import save_document,save_analysis
 from backend.orchestration.orchestrator import analyze
 from frontend.dashboard import PAGES
 uid=register('reviewer','p','p');did,_=save_document(uid,sample);save_analysis(uid,did,analyze(sample))
 at=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'));at.session_state['user_id']=uid;at.session_state['username']='reviewer';at.run(timeout=30)
 for page in PAGES:
  at.sidebar.radio[0].set_value(page).run(timeout=30)
  assert not at.exception, page
  assert not at.error, [(page,e.value) for e in at.error]

def test_registration_login_logout():
 at=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py')).run(timeout=30)
 at.text_input(key='new_user').set_value('ui-user');at.text_input(key='new_pw').set_value('p')
 next(t for t in at.text_input if t.label=='Confirm password').set_value('p')
 next(b for b in at.button if b.label=='Create Account').click().run(timeout=30)
 assert at.success
 next(t for t in at.text_input if t.label=='Username' and t.key!='new_user').set_value('ui-user')
 next(t for t in at.text_input if t.label=='Password' and t.key!='new_pw').set_value('p')
 next(b for b in at.button if b.label=='Login').click().run(timeout=30)
 assert at.session_state['user_id']
 next(b for b in at.button if b.label=='Logout').click().run(timeout=30)
 assert any(b.label=='Login' for b in at.button)
def test_sample_upload():
 from backend.authentication.auth import register
 from backend.database.db_operations import documents
 uid=register('uploader','p','p')
 at=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'));at.session_state['user_id']=uid;at.session_state['username']='uploader';at.run(timeout=30)
 at.sidebar.radio[0].set_value('Upload Clinical Protocol').run(timeout=30)
 at.checkbox[0].set_value(True).run(timeout=30)
 next(b for b in at.button if b.label=='Analyze protocol').click().run(timeout=30)
 assert not at.error;assert len(documents(uid))==1;assert documents(uid)[0].status=='Completed'
