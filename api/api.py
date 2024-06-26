import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api

from models import db
from views.view_task import ViewTask
from views.view_tasks import ViewTasks
from views.view_video import ViewVideo
from views.view_signup import ViewSignUp
from views.view_login import ViewLogin
from views.view_health import ViewHealth

host = os.environ.get('HOST_PG', 'localhost')
port = os.environ.get('PORT_PG', 5432)
user = os.environ.get('USER_PG', 'postgres')
password = os.environ.get('PWD_PG', 'postgres')
database_name = os.environ.get('DB_NAME_PG', 'videos')

jwt = JWTManager()

def create_flask_app():
    _app = Flask(__name__)
    _app.config['PROPAGATE_EXCEPTIONS'] = True
    _app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user}:{password}@{host}:{port}/{database_name}'
    _app.config['JWT_SECRET_KEY'] = 'frase-secreta'
    # _app.config['SQLALCHEMY_POOL_SIZE'] = 20
    # _app.config['SQLALCHEMY_MAX_OVERFLOW'] = 100
    app_context = _app.app_context()
    app_context.push()
    add_urls(_app)
    CORS(
        _app,
        origins="*",
    )

    return _app


def add_urls(_app):
    api = Api(_app)
    api.add_resource(ViewHealth, '/')
    api.add_resource(ViewSignUp, '/api/auth/signup')
    api.add_resource(ViewLogin, '/api/auth/login')
    api.add_resource(ViewTasks, '/api/tasks')
    api.add_resource(ViewTask, '/api/tasks/<int:id_task>')
    api.add_resource(ViewVideo, '/api/videos')


app = create_flask_app()
db.init_app(app)
jwt.init_app(app)
db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 6000), debug=False)
