from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(80), unique=True, nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<Token {self.device_name}>'
    
    def __init__(self, device_name, token):
        self.device_name = device_name
        self.token = token
