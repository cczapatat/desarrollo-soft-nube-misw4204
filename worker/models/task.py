import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime

from .declarative_base import Base


class Status(enum.Enum):
    UPLOADED = 'uploaded'
    PROCESSED = 'processed'
    ERROR = 'error'


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), nullable=False)
    file_name = Column(String(500), nullable=False)
    path_origin = Column(Text, nullable=False)
    path_processed = Column(Text, nullable=True)
    status = Column(Enum(Status))
    created_at = Column(DateTime(), default=datetime.now)
    updated_at = Column(DateTime(), default=datetime.now)
