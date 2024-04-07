import os
from datetime import datetime
from faker import Faker
import stomp
from models.models import Task, Status
from models.models import db

from flask import request
from flask_restful import Resource

video_ext = os.environ.get('IN_EXT_VIDEOS', 'mp4')

dirname = os.path.dirname(__file__)
dir_frames = '{}/../frames'.format(dirname)

in_result_path = os.environ.get('IN_FILE_VIDEOS', '')
is_in_result_path_filled = len(in_result_path) > 0

if is_in_result_path_filled:
    in_result_file = in_result_path
else:
    in_result_file = '{}/../../videos/ins'.format(dirname)

faker = Faker()

# ActiveMQ configuration
host = os.environ.get('HOST_QUEUE', 'localhost')
port = os.environ.get('PORT_QUEUE', 61613)
hosts = [(host, port)]
name_queue = os.environ.get('NAME_QUEUE', 'worker')
user_queue = os.environ.get('USER_QUEUE', 'admin')
password_queue = os.environ.get('PWD_QUEUE', 'admin')
cliente_queue = 'api'


def stomp_connect(_conn):
    _conn.connect(user_queue, password_queue, wait=True, headers={'client-id': cliente_queue})
    print('[Queue] New Connection')


def stomp_send(body):
    print('[Queue] STARTING ENQUEUEING TO {0}'.format(name_queue))
    conn.send(
        body=str(body),
        destination='/queue/{0}'.format(name_queue),
        persistent=True,
        headers={'persistent': "true"},
    )
    print('[Queue] Send new task')


class ConnectionListener(stomp.ConnectionListener):
    def __init__(self, _conn):
        self._conn = _conn

    @staticmethod
    def on_error(message):
        print('[Queue] received an error "%s"' % message)

    def on_disconnected(self):
        print('[Queue] Queue disconnected')
        stomp_connect(self._conn)


conn = stomp.Connection(host_and_ports=hosts)
conn.set_listener('list', ConnectionListener(conn))


class ViewTasks(Resource):
    def __init__(self):
        stomp_connect(conn)

    @staticmethod
    def post():
        input_form = request.form
        print('[Http] Starting request')
        # Check if the request is associated to a user
        if input_form.get('id', None) is None:
            return {
                'id': None,
                'result': {'error': 'data incomplete', 'details': {}, 'id': 'invalid'},
            }, 400
        user_id = input_form.get('id')
        # Check if the request contains a file
        if 'file' not in request.files:
            return {
                'id': user_id,
                'result': {'error': 'no file part', 'details': {}, 'id': 'user_id'},
            }, 400

        file = request.files['file']

        # Check if the file is empty
        if file.filename == '':
            return {
                'id': user_id,
                'result': {'error': 'no file part', 'details': {}, 'id': 'user_id'},
            }, 400
        filename_origin = file.filename
        print('[NewTask] userId: {}, fileOriginName: {}'.format(user_id, filename_origin))

        try:
            date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            uuid = faker.unique.iban()
            path = '{}/{}_{}.{}'.format(in_result_file, date, uuid, video_ext)

            print('[NewTask] userId: {}, fileOriginName: {}, to path: {}'.format(user_id, filename_origin, path))

            # save video to folder
            file.save(path)
            print('[NewTask] saved userId: {}, fileOriginName: {}'.format(user_id, filename_origin))

            # save task
            task = Task(user_id=int(user_id), file_name=filename_origin, path_origin=path, status=Status.UPLOADED)
            db.session.add(task)
            db.session.commit()

            # Send task to queue
            stomp_send({'id': task.id})

            return {
                'id': task.id,
                'result': {'success': 'file was received successfully', 'details': {}, 'id': user_id}
            }, 200

        except Exception as ex:
            print('[Api][upload_new_video] error {}'.format(str(ex)))
            return {
                'id': None,
                'result': {'error': str(ex), 'details': {}, 'status': 'Error'},
            }, 400
