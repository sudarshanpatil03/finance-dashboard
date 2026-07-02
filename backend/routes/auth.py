from flask import Blueprint, request, jsonify
from models import db, User, Category
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps

auth_bp = Blueprint('auth', __name__)


# ── Helper: create JWT token ──────────────────
def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm='HS256')


# ── Helper: protect routes with @token_required ──
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated


# ── POST /api/register ────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validate required fields
    if not data or not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Name, email and password are required'}), 400

    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    # Hash password
    hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

    # Create user
    user = User(
        name=data['name'],
        email=data['email'],
        password_hash=hashed.decode('utf-8')
    )
    db.session.add(user)
    db.session.flush()   # get user.id before commit

    # Auto-create default categories for this user
    default_categories = [
        ('Salary',       'income'),
        ('Freelance',    'income'),
        ('Other Income', 'income'),
        ('Food',         'expense'),
        ('Rent',         'expense'),
        ('Transport',    'expense'),
        ('Shopping',     'expense'),
        ('Healthcare',   'expense'),
        ('Education',    'expense'),
        ('Entertainment','expense'),
    ]
    for name, cat_type in default_categories:
        db.session.add(Category(user_id=user.id, name=name, type=cat_type))

    db.session.commit()

    token = create_token(user.id)
    return jsonify({
        'message': 'User registered successfully',
        'token': token,
        'user': user.to_dict()
    }), 201


# ── POST /api/login ───────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    # Check password
    if not bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = create_token(user.id)
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    }), 200


# ── GET /api/me ───────────────────────────────
@auth_bp.route('/me', methods=['GET'])
@token_required
def get_me(current_user):
    return jsonify({'user': current_user.to_dict()}), 200
