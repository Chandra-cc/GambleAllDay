from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth

# Initialize the app and configurations
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
oauth = OAuth(app)

# Register Google OAuth with proper OIDC metadata
google = oauth.register(
    'google',
    client_id='your_google_client_id',
    client_secret='your_google_client_secret',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid profile email'},
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",  # Metadata URL for Google
    issuer='https://accounts.google.com',  # Explicitly specify the issuer URL
)

# Import routes (after app is initialized)
from app import routes
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth

# Initialize the app and configurations
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
oauth = OAuth(app)

# Register Google OAuth with proper OIDC metadata
google = oauth.register(
    'google',
    client_id='813875452342-17cu2ik4d6sfmucbvtjiijsco98h6gkt.apps.googleusercontent.com',
    client_secret='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',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid profile email'},
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",  # Metadata URL for Google
    issuer='https://accounts.google.com',  # Explicitly specify the issuer URL
)

# Import routes (after app is initialized)
from app import routes
