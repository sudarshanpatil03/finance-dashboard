from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# ── Manual CORS — works with all flask-cors versions ──
@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin', '')
    if origin in ('http://localhost:3000', 'http://127.0.0.1:3000', 'https://finance-dash-sudarshan.web.app'):
        response.headers['Access-Control-Allow-Origin']  = origin
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        origin = request.headers.get('Origin', '')
        if origin in ('http://localhost:3000', 'http://127.0.0.1:3000', 'https://finance-dash-sudarshan.web.app'):
            response.headers['Access-Control-Allow-Origin']  = origin
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response, 200

from models import db
db.init_app(app)

# Create all tables if they don't exist
with app.app_context():
    db.create_all()

from routes.auth import auth_bp
from routes.transactions import transactions_bp
from routes.budgets import budgets_bp
from routes.debts import debts_bp
from routes.dashboard import dashboard_bp

app.register_blueprint(auth_bp,          url_prefix='/api')
app.register_blueprint(transactions_bp,  url_prefix='/api')
app.register_blueprint(budgets_bp,       url_prefix='/api')
app.register_blueprint(debts_bp,         url_prefix='/api')
app.register_blueprint(dashboard_bp,     url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
