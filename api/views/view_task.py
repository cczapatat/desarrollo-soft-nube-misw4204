from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from models.models import Task, TaskSchema, db
from utils.url_util import create_url_to_public
from utils.delete_file import remove_file

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


    @jwt_required()
    def delete(self, id_task):
        user_id = get_jwt_identity()

        results = []

        task = Task.query.filter(Task.id == id_task).one_or_none()

        if task is not None:

            if task.user_id != user_id:
                return {'message': 'forbidden access to task'}, 401

            try:
                #delete the files only if those exists in the os
                #with the os

                removed_origin = False
                removed_processed = False

                if task.path_origin is not None:
                     removed_origin = remove_file(task.path_origin)

                if task.path_processed is not None:
                    removed_processed = remove_file(task.path_processed)

                if removed_origin or removed_processed:
                    db.session.delete(task)
                    db.session.commit()
                    results.insert({'success': 'task was deleted', 'id': task.id})
            except Exception as ex:
                results.insert({'error': "A problem ocurred while deleting the task" , 'id': task.id})
            finally:
                return results, 200
        else:
            return {'message': 'not found'}, 404


