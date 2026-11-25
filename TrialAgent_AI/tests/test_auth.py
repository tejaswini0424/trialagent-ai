import pytest
from sqlalchemy import select
from backend.authentication.auth import register,login
from backend.database.models import User
def test_registration_and_login(database):
 uid=register('a','x','x');assert login('a','x')==uid;assert login('a','wrong') is None
 with database() as s: assert s.scalar(select(User)).password_hash.startswith('$2')
def test_duplicate_and_confirmation():
 register('name','p','p')
 with pytest.raises(ValueError): register('name','p','p')
 with pytest.raises(ValueError): register('other','p','q')
@pytest.mark.parametrize('username,password',[(' ',' '),('用户','🔒'*100),('x','a')])
def test_unrestricted_nonempty(username,password):
 assert login(username,password) is None
 uid=register(username,password,password);assert login(username,password)==uid
@pytest.mark.parametrize('u,p',[('','x'),('x','')])
def test_empty_rejected(u,p):
 with pytest.raises(ValueError): register(u,p,p)
