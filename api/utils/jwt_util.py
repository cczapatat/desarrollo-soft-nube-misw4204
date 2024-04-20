import os
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

api_key_value = os.environ.get('API_KEY', 'ApiKeyTestLoadGp10')

@jwt_required()
def jwt_protection():
   pass

def get_user_id():
    api_key = request.headers.get('ApiKey', None)
    user_id_header = request.headers.get('UserId', None)
    if api_key != api_key_value or user_id_header is None:
        jwt_protection()
        user_id = get_jwt_identity()
    else:
        user_id = user_id_header

    return user_id