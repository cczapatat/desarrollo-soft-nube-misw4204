import enum
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, UniqueConstraint
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

class User(db.Model):
    __tablename__ = 'users'

    __table_args__ = (
        UniqueConstraint('email', name='unique_email'),
        UniqueConstraint('username', name='unique_username'),
    )
    id = Column(Integer(), primary_key=True)
    email = Column(String(100), nullable=False)
    username = Column(String(50), nullable=False)
    password =  Column(String(500), nullable=False)

    def hash_password(self):
        self.password = generate_password_hash(self.password, 'sha256')

    def check_password(self, clave):
        return check_password_hash(self.password, clave)



class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
        exclude = ('password',)

class TaskSchema(SQLAlchemyAutoSchema):
    status = fields.Enum(Status, by_value=True, allow_none=False)

    class Meta:
        model = Task
        include_relationships = True
        include_fk = True
        load_instance = True
