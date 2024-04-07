import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Status(enum.Enum):
    UPLOADED = 'uploaded'
    PROCESSED = 'processed'
    ERROR = 'error'


class Task(db.Model):
    __tablename__ = 'tasks'

    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), nullable=False)
    file_name = Column(String(500), nullable=False)
    path_origin = Column(Text, nullable=False)
    path_processed = Column(Text, nullable=True)
    status = Column(Enum(Status))
    created_at = Column(DateTime(), default=datetime.now)
    updated_at = Column(DateTime(), default=datetime.now)


class TaskSchema(SQLAlchemyAutoSchema):
    status = fields.Enum(Status, by_value=True, allow_none=False)

    class Meta:
        model = Task
        include_relationships = True
        include_fk = True
        load_instance = True
