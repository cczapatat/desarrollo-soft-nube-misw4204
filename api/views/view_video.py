import os
from flask import request, send_file
from flask_restful import Resource


class ViewVideo(Resource):

    def get(self):
        path = request.args.get('path', default=None)

        if path is None:
            return {'message': 'path is require'}, 400

        if not os.path.exists(path):
            return {'message': 'not found'}, 404

        return send_file(path, as_attachment=True)
