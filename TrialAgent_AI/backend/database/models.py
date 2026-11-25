from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, UniqueConstraint
from backend.database.db_connection import Base
def now(): return datetime.now(timezone.utc)
class User(Base):
 __tablename__='users'
 id=Column(Integer,primary_key=True); username=Column(String,unique=True,nullable=False); password_hash=Column(String,nullable=False); created_at=Column(DateTime,default=now)
class Document(Base):
 __tablename__='documents'
 __table_args__=(UniqueConstraint('user_id','digest'),)
 id=Column(Integer,primary_key=True); user_id=Column(Integer,ForeignKey('users.id'),nullable=False); filename=Column(String); file_type=Column(String); digest=Column(String); uploaded_at=Column(DateTime,default=now); status=Column(String,default='Pending'); content=Column(Text); analysis=Column(Text)
class AgentResult(Base):
 __tablename__='agent_results'
 id=Column(Integer,primary_key=True); document_id=Column(Integer,ForeignKey('documents.id')); agent_name=Column(String); status=Column(String); output=Column(Text); duration=Column(Float)
class FindingRecord(Base):
 __tablename__='findings'
 id=Column(Integer,primary_key=True); document_id=Column(Integer,ForeignKey('documents.id')); agent_name=Column(String); severity=Column(String); category=Column(String); description=Column(Text); evidence=Column(Text); page=Column(Integer,nullable=True); review_status=Column(String); payload=Column(Text)
class AnalysisHistory(Base):
 __tablename__='analysis_history'
 id=Column(Integer,primary_key=True); user_id=Column(Integer,ForeignKey('users.id')); document_id=Column(Integer,ForeignKey('documents.id')); created_at=Column(DateTime,default=now); summary=Column(Text)
