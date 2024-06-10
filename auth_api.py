import os
import jwt
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from util import sanitize_request_content, device_already_exists
from model import db, Token
from datetime import datetime, timezone, timedelta

load_dotenv()

auth_api = Blueprint('auth_api', __name__)

@auth_api.route('/register-device', methods=['POST'])
@device_already_exists
def generate_auth_token():
    try:
        device_name = sanitize_request_content(request.json['device_name'])
        secret_hash = sanitize_request_content(request.json['secret_hash'])
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    new_token = Token(device_name=device_name, token=secret_hash)
    db.session.add(new_token)
    db.session.commit()

    return jsonify({'token_content': new_token.__repr__(), 'message': 'Token generated successfully!'}), 201

@auth_api.route('/generate-auth-token', methods=['POST'])
def authenticate():
    try:
        device_name = sanitize_request_content(request.json['device_name'])
        secret_hash = sanitize_request_content(request.json['secret_hash'])
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    token_entry = Token.query.filter_by(device_name=device_name, token=secret_hash).first()

    if token_entry:
        token_payload = {
            'device_name': token_entry.device_name,
            'exp': datetime.now(timezone.utc) + timedelta(days=1)
        }

        jwt_token = jwt.encode(token_payload, os.environ.get('SECRET_KEY'), algorithm='HS256')

        return jsonify({'token': jwt_token}), 200
    else:
        return jsonify({'message': 'Unauthorized!'}), 401
    
@auth_api.route('/refresh-auth-token', methods=['POST'])
def refresh_auth_token():
    try:
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=['HS256'])
            token_entry = Token.query.filter_by(device_name=data['device_name']).first()

            if token_entry:
                token_payload = {
                    'device_name': token_entry.device_name,
                    'exp': datetime.now(timezone.utc) + timedelta(days=1)
                }

                jwt_token = jwt.encode(token_payload, os.environ.get('SECRET_KEY'), algorithm='HS256')

                return jsonify({'token': jwt_token}), 200
            else:
                return jsonify({'message': 'Unauthorized!'}), 401

        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 400

