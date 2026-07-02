from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000", "https://finance-dash-sudarshan.web.app"]}}, supports_credentials=True)

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
