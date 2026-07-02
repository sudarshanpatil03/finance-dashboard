import os
import urllib.parse
from dotenv import load_dotenv
load_dotenv()

class Config:
    user = os.getenv('DB_USER', '')
    pwd  = os.getenv('DB_PASSWORD', '')
    if pwd:
        pwd = urllib.parse.quote_plus(pwd)
    host = os.getenv('DB_HOST', '')
    db   = os.getenv('DB_NAME', '')

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{user}:{pwd}@{host}/{db}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET = os.getenv('JWT_SECRET', 'fallback_secret')
