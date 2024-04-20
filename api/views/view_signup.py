from flask import request
from datetime import timedelta
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from models.models import User, db
from sqlalchemy import or_


class ViewSignUp(Resource):
    def post(self):
        if User.query.filter(or_(User.email==request.json['email'], User.username==request.json['username'],)).first() is not None:
            return {'message': f'email ({request.json["email"]} or username ({request.json["username"]}) already was signed up'}, 400
        
        if request.json['username'] == '' or request.json['password1'] == '' or request.json['password2'] == '' or request.json['email'] == '':
            return {'message': 'Invalid fields'}, 400
        
        if request.json['password1'] != request.json['password2']:
            return {'message': 'password1 and password2 does not match'}, 400
        
        new_user = User(
            email = request.json['email'],
            username = request.json['username'],
            password = request.json['password1'],
        )

        new_user.hash_password()

        try:
            db.session.add(new_user)
            db.session.commit()

            user = User.query.filter(User.email==request.json['email']).first()

            access_token = create_access_token(identity = user.id, expires_delta = timedelta(days = 1))
            
            return {
                'message':'user created',
                'access_token': access_token
            }, 200
        
        except:
            return {'message':'An error has occurred'}, 500
