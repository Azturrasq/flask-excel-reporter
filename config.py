import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_default_secret_key'
    UPLOAD_FOLDER = 'data/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limit upload size to 16 MB
    ALLOWED_EXTENSIONS = {'xls', 'xlsx'}
    
    # Database configuration (if needed in the future)
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Other configurations can be added here as needed
