import os
import tempfile
from datetime import datetime
from faker import Faker
from models.models import Task, Status, User, TaskSchema
from models.models import db
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask import request
from flask_restful import Resource
from utils.jwt_util import get_user_id
from utils.storage import upload_file
from werkzeug.utils import secure_filename
from google.cloud import pubsub_v1

video_ext = os.environ.get('IN_EXT_VIDEOS', 'mp4')

dirname = os.path.dirname(__file__)
dir_frames = '{}/../frames'.format(dirname)

in_result_path = os.environ.get('IN_FILE_VIDEOS', '')
in_result_path_gs = os.environ.get('IN_GS_FILE_VIDEOS')
is_in_result_path_filled = len(in_result_path) > 0

if is_in_result_path_filled:
    in_result_file = in_result_path
else:
    in_result_file = '{}/../../videos/ins'.format(dirname)

faker = Faker()
task_schema = TaskSchema()

# ActiveMQ configuration
host = os.environ.get('HOST_QUEUE', 'localhost')
port = os.environ.get('PORT_QUEUE', 61613)
hosts = [(host, port)]
name_queue = os.environ.get('NAME_QUEUE', 'videos')
user_queue = os.environ.get('USER_QUEUE', 'admin')
password_queue = os.environ.get('PWD_QUEUE', 'admin')
date_queue = datetime.now().strftime("%Y%m%d%H%M%S%f")
cliente_queue = 'api{}{}'.format(faker.unique.iban(), date_queue)
queue_cloud_provider = os.environ.get('QUEUE_CLOUD_PROVIDER')
project_id = os.environ.get('GCLOUD_PROJECT')
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, name_queue)


def get_file_path(filename):
    file_name = secure_filename(filename)
    return os.path.join(tempfile.gettempdir(), file_name)


def publish_messages_data(message: str) -> None:
    future = publisher.publish(topic_path, message.encode("utf-8"))
    print(future.result())

    print(f"Published messages to {topic_path}.")


class ViewTasks(Resource):


    @staticmethod
    def post():
        print('[Http] Starting request')

        # Check if the request is associated to a user
        user_id = get_user_id()
        user = User.query.get(user_id)

        if user is None:
            return {'message': 'User not found'}, 400

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
            uuid = faker.unique.iban()
            name_file = '{}_{}'.format(uuid, filename_origin)
            file.save(get_file_path(name_file))
            date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            path2 = '{}/{}_{}.{}'.format(in_result_path_gs, date, uuid, video_ext)

            print('[NewTask] userId: {}, fileOriginName: {}, to path: {}'.format(user_id, filename_origin, path2))

            upload_file(get_file_path(name_file), path2)
            print("Processed file: %s" % name_file)

            file_path = get_file_path(name_file)
            if os.path.exists(file_path):
                os.remove(file_path)

            print('[NewTask] saved userId: {}, fileOriginName: {}'.format(user_id, filename_origin))

            # save task
            task = Task(user_id=int(user_id), file_name=filename_origin, path_origin=path2, status=Status.UPLOADED)
            db.session.add(task)
            db.session.commit()

            data = {'id': task.id, 'path_origin': task.path_origin, 'path_origin_gs': path2}
            publish_messages_data(str(data))


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

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        tasks = []

        # if max parameter is passed, then limit the number of tasks to return
        max_tasks = request.args.get('max', None)
        if max_tasks is not None:
            try:
                max_tasks = int(max_tasks)
            except:
                max_tasks = 100

            if max_tasks > 0:
                tasks = Task.query.filter(Task.user_id == user_id).limit(max_tasks).all()

        # if order parameter is passed, then order the tasks, by asc or desc
        order_by = request.args.get('order', None)

        if order_by is not None:
            if order_by == '0':
                # order by desc if filter equals to 0
                tasks = Task.query.filter(Task.user_id == user_id).order_by(Task.id.desc()).all()
            elif order_by == '1':
                # order by asc if filter equals to 1
                tasks = Task.query.filter(Task.user_id == user_id).order_by(Task.id.asc()).all()

        if max_tasks is None and order_by is None:
            tasks = Task.query.filter(Task.user_id == user_id).all()

        data_response = task_schema.dump(tasks, many=True)

        # return tasks as dictionary in json
        return data_response, 200
