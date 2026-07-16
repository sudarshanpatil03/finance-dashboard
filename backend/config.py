import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # Neon/Render provide a full DATABASE_URL — use it directly if available
    _db_url = os.getenv('DATABASE_URL', '')

    # Neon connection strings start with "postgresql://", SQLAlchemy needs "postgresql+psycopg2://"
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
    elif _db_url.startswith('postgresql://'):
        _db_url = _db_url.replace('postgresql://', 'postgresql+psycopg2://', 1)

    SQLALCHEMY_DATABASE_URI = _db_url or 'sqlite:///finance_local.db'  # local fallback
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET = os.getenv('JWT_SECRET', 'fallback_secret')
