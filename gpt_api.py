import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify, send_from_directory, abort
from openai import OpenAI
from util import sanitize_request_content, auth_protected

load_dotenv()

gpt_api = Blueprint('gpt_api', __name__)
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

@gpt_api.route('/')
@auth_protected
def index():
    return jsonify({'message': 'TradingView API integration with OpenAI GPT-4o API!'})

@gpt_api.route('/prompt', methods=['POST'])
@auth_protected
def gpt_api_endpoint():
    try:
        system_content = sanitize_request_content(request.json['system_content'])
        user_content = sanitize_request_content(request.json['user_content'])
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    chat = client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {'role': 'system', 'content': system_content},
            {'role': 'user', 'content': user_content},
        ]
    )

    response_content = chat.choices[0].message.content
    file_name = f'gpt-api-repsonse-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.md'

    os.makedirs('responses', exist_ok=True)
    with open (os.path.join('responses', file_name), 'a+') as f:
        f.write(response_content)

    return jsonify({'response_content': f"{os.environ.get('DEVELOPMENT_URI')}:{os.environ.get('PORT')}/api/v1/gpt/res/{file_name}" if os.environ.get('FLASK_ENV') == 'development' else None}), 200

@gpt_api.route('/res/<path:file_name>', methods=['GET'])
@auth_protected
def get_response(file_name):
    try:
        file_path = os.path.join('responses', file_name)
        if not os.path.exists(file_path):
            abort(404, description="File not found")
        
        return send_from_directory('responses', file_name, as_attachment=False)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
