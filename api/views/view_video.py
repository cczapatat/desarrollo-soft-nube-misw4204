import os
from flask import request, send_file
from flask_restful import Resource
from datetime import datetime, timedelta
from utils.storage import generate_signed_url


class ViewVideo(Resource):

    def get(self):
        path = request.args.get('path', default=None)

        if path is None:
            return {'message': 'path is require'}, 400

        object_name = path
        current_time = datetime.now()
        signed_url = generate_signed_url(object_name, expiration=current_time + timedelta(seconds=3600))

        if not signed_url:
            return {'message': 'not found'}, 404

        return {'message': signed_url}, 200
