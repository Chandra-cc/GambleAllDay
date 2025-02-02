# Import routes (after app is initialized)
from app import routes
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
load_dotenv()

# Initialize the app and configurations
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
oauth = OAuth(app)

import os

google = oauth.register(
    'google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid profile email'},
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    issuer='https://accounts.google.com',
)

# Import routes (after app is initialized)
from app import routes
