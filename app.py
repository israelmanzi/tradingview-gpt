import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from gpt_api import gpt_api
from auth_api import auth_api
from model import db

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['DEVELOPMENT_URI'] = os.environ.get('DEVELOPMENT_URI')
app.config['FLASK_ENV'] = os.environ.get('FLASK_ENV')
app.config['PORT'] = os.environ.get('PORT')
app.app_context().push()
db.init_app(app)

app.register_blueprint(auth_api, url_prefix='/api/v1/auth')
app.register_blueprint(gpt_api, url_prefix='/api/v1/gpt')

if __name__ == '__main__':
    app.run(debug=True, port=app.config['PORT'])
