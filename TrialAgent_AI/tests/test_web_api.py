import pytest
from fastapi.testclient import TestClient
@pytest.fixture
def client(monkeypatch):
 import web.api as web
 monkeypatch.setattr(web,'ready',lambda:None)
 return TestClient(web.app)
def signup(client,name='web-user'):
 assert client.post('/api/register',json={'username':name,'password':'p','confirmation':'p'}).status_code==200
 assert client.post('/api/login',json={'username':name,'password':'p'}).status_code==200
def test_auth_and_session(client):
 assert client.get('/api/documents').status_code==401
 signup(client);assert client.get('/api/me').json()['username']=='web-user'
 assert 'httponly' in client.cookies.get('trialagent_session','') or client.cookies.get('trialagent_session')
 client.post('/api/logout');assert client.get('/api/me').status_code==401
def test_sample_exports_and_history(client):
 signup(client);response=client.post('/api/sample',json={});assert response.status_code==200,response.text
 did=response.json()['id'];assert client.get('/api/documents').json()[0]['status']=='Completed'
 assert len(client.get('/api/documents/'+str(did)).json()['analysis']['agents'])==7
 for kind in ['pdf','csv','json']:
  r=client.get(f'/api/documents/{did}/export/{kind}');assert r.status_code==200;assert r.content
 assert len(client.get('/api/history').json())==1
 assert client.post(f'/api/documents/{did}/reanalyze',json={}).json()['duplicate']
def test_upload_validation_and_ownership(client):
 signup(client,'owner');r=client.post('/api/analyze',files={'file':('x.txt',b'Study title: Test protocol')});assert r.status_code==200,r.text
 did=r.json()['id']
 assert client.post('/api/analyze',files={'file':('bad.exe',b'text')}).status_code==400
 assert client.post('/api/analyze',files={'file':('empty.txt',b'')}).status_code==400
 client.post('/api/logout');signup(client,'other')
 assert client.get(f'/api/documents/{did}').status_code==404
 assert client.get(f'/api/documents/{did}/export/json').status_code==404
 assert client.post(f'/api/documents/{did}/reanalyze',json={}).status_code==404
def test_security_and_validation(client):
 assert client.get('/').status_code==200
 r=client.get('/assets/app.js');assert r.status_code==200;assert 'nosniff'==r.headers['x-content-type-options']
 assert client.get('/assets/.env').status_code==404
 assert client.post('/api/login',json={},headers={'origin':'https://evil.example'}).status_code==403
 signup(client)
 assert client.post('/api/sample',json={'checklist':{'bad':True}}).status_code==400
 assert client.get('/api/checklist').status_code==200
