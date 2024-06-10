import os
import jwt
import hashlib
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from util import sanitize_request_content, device_already_exists, auth_protected
from model import db, Token
from datetime import datetime, timezone, timedelta

load_dotenv()

auth_api = Blueprint('auth_api', __name__)

@auth_api.route('/get-auth-info', methods=['GET'])
@auth_protected
def fetch_device_info(raw_token=None):
    try:
        token_payload = jwt.decode(raw_token, os.environ.get('SECRET_KEY'), algorithms=['HS256'])

        token_entry = Token.query.filter_by(device_name=token_payload['device_name']).first()
        return jsonify({'info': token_entry.__repr__()}), 200
    except jwt.InvalidTokenError or jwt.ExpiredSignatureError:
        return jsonify({'message': 'Unauthorized!'}), 401
    
@auth_api.route('/generate-hash', methods=['GET'])
def generate_hash():
    sha = hashlib.sha256()
    curr_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sha.update(curr_time.encode())
    return sha.hexdigest()


@auth_api.route('/register-device', methods=['POST'])
@device_already_exists
def register_device():
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
    
    print(device_name, secret_hash)

    tokens = Token.query.all()
    token_entry = Token.query.filter_by(token=secret_hash, device_name=device_name).first()

    print(tokens)

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

