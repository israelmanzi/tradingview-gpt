import os
import jwt
from functools import wraps
from flask import g, request, abort
from model import Token

def auth_protected(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            abort(401, description='Unauthorized!')

        raw_token = token.split(' ')[1]

        try:
            data = jwt.decode(raw_token, os.environ.get('SECRET_KEY'), algorithms=['HS256'])
            g.device_name = data['device_name']
            kwargs['raw_token'] = raw_token
        except jwt.ExpiredSignatureError:
            abort(401, description='Token has expired!')
        except jwt.InvalidTokenError:
            abort(401, description='Invalid token!')
        
        return f(*args, **kwargs)
    
    return decorated

def device_already_exists(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        device_name = sanitize_request_content(request.json['device_name'])
        token_entry = Token.query.filter_by(device_name=device_name).first()
        
        if token_entry:
            abort(409, description='Device already exists!')
        
        return f(*args, **kwargs)
    
    return decorated

def sanitize_request_content(content):
    if not isinstance(content, str) or not content.strip():
        abort(400, description='Invalid request content!')
    return content  
