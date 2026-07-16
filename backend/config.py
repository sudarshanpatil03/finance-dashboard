import os
import ssl
from dotenv import load_dotenv
load_dotenv()

class Config:
    # Neon/Render provide a full DATABASE_URL
    _db_url = os.getenv('DATABASE_URL', '')

    # Switch to pg8000 dialect (pure Python, works on Python 3.14)
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql+pg8000://', 1)
    elif _db_url.startswith('postgresql://'):
        _db_url = _db_url.replace('postgresql://', 'postgresql+pg8000://', 1)

    # pg8000 does NOT support ?sslmode= in the URL — strip it out
    if '?sslmode=' in _db_url:
        _db_url = _db_url.split('?sslmode=')[0]

    SQLALCHEMY_DATABASE_URI = _db_url or 'sqlite:///finance_local.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET = os.getenv('JWT_SECRET', 'fallback_secret')

    # Pass SSL via connect_args for pg8000 (required by Neon)
    if os.getenv('DATABASE_URL'):
        _ssl_ctx = ssl.create_default_context()
        _ssl_ctx.check_hostname = False
        _ssl_ctx.verify_mode = ssl.CERT_NONE
        SQLALCHEMY_ENGINE_OPTIONS = {'connect_args': {'ssl_context': _ssl_ctx}}
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {}
