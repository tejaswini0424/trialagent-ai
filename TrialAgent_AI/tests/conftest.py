import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import tempfile
_runtime_tmp=Path(__file__).resolve().parents[1]/'.pytest-runtime'
_runtime_tmp.mkdir(exist_ok=True)
tempfile.tempdir=str(_runtime_tmp)
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.db_connection import Base
from backend.database import models
@pytest.fixture(autouse=True)
def database(tmp_path,monkeypatch):
 engine=create_engine('sqlite:///'+str(tmp_path/'test.db'));Base.metadata.create_all(engine)
 factory=sessionmaker(engine,expire_on_commit=False)
 import backend.authentication.auth as auth
 import backend.database.db_operations as ops
 monkeypatch.setattr(auth,'Session',factory);monkeypatch.setattr(ops,'Session',factory)
 yield factory
 engine.dispose()
@pytest.fixture
def sample():
 from backend.document_processing.document_loader import load_document
 return load_document('sample.txt',(Path(__file__).resolve().parents[1]/'data/sample_protocol.txt').read_bytes())
