import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgresSQL configuration
host = os.environ.get('HOST_PG', 'localhost')
port = os.environ.get('PORT_PG', 5432)
user = os.environ.get('USER_PG', 'postgres')
password = os.environ.get('PWD_PG', 'postgres')
database_name = os.environ.get('DB_NAME_PG', 'videos')

url = URL.create(
    drivername="postgresql",
    host=host,
    port=port,
    username=user,
    password=password,
    database=database_name
)
engine = create_engine(url)
Session = sessionmaker(bind=engine)

Base = declarative_base()
session = Session()
