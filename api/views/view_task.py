from flask_restful import Resource
from models.models import Task, TaskSchema
from utils.url_util import create_url_to_public
from flask_jwt_extended import get_jwt_identity, jwt_required

task_schema = TaskSchema()


class ViewTask(Resource):
    
    @jwt_required()
    def get(self, id_task):
        user_id = get_jwt_identity()
        task = Task.query.filter(Task.id == id_task).one_or_none()

        if task is None:
            return {'message': 'not found'}, 404
        
        if task.user_id != user_id:
            return {'message': 'forbbiden access to task'}, 401

        data_response = task_schema.dump(task)
        data_response['url_recovery'] = create_url_to_public(task.path_origin)
        data_response['url_download'] = create_url_to_public(task.path_processed)

        return data_response, 200
