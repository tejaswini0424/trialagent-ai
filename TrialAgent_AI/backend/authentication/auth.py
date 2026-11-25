import bcrypt, hashlib
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from backend.database.db_connection import Session
from backend.database.models import User
def secret(password):
 return hashlib.sha256(password.encode('utf-8')).hexdigest().encode('ascii')
def register(username,password,confirmation):
 if not username or not password: raise ValueError('Username and password cannot be empty.')
 if password != confirmation: raise ValueError('Passwords must match.')
 with Session() as s:
  user=User(username=username,password_hash=bcrypt.hashpw(secret(password),bcrypt.gensalt()).decode())
  s.add(user)
  try: s.commit()
  except IntegrityError: s.rollback(); raise ValueError('Username already exists.')
  return user.id
def login(username,password):
 with Session() as s:
  u=s.scalar(select(User).where(User.username==username))
  return u.id if u and bcrypt.checkpw(secret(password),u.password_hash.encode()) else None
