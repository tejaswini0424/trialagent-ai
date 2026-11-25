import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv('TRIALAGENT_DB') or os.getenv('DATABASE_URL') or 'sqlite:///trialagent.db'
if DATABASE_URL.startswith('postgres://'): DATABASE_URL = DATABASE_URL.replace('postgres://','postgresql+psycopg://',1)
elif DATABASE_URL.startswith('postgresql://'): DATABASE_URL = DATABASE_URL.replace('postgresql://','postgresql+psycopg://',1)
MAX_UPLOAD_MB = int(os.getenv('MAX_UPLOAD_MB', '20'))
DISCLAIMER = 'Research and education only. Automated findings identify documentation review needs, not regulatory violations or certification. Qualified professionals must review all conclusions.'
