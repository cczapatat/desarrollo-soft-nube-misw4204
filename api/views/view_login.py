from flask import request
from datetime import timedelta
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from models.models import User, db
from sqlalchemy import or_


class ViewLogin(Resource):
    def post(self):
        user = User.query.filter(User.username == request.json['username']).first()

        if user is None:
            return {'message':f'does not exist an user with username ({request.json["username"]})'}, 400
        
        if not user.check_password(request.json['password']):
            return {'message': 'Incorrect Password'}, 400
        
        try:
            access_token = create_access_token(identity = user.id, expires_delta = timedelta(days = 1))
            return {
                'message':'Session started',
                'access_token':access_token
            }, 200
        
        except:
            return {'message':'An error has occurred'}, 500
