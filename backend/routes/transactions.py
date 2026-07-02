from flask import Blueprint, request, jsonify
from models import db, Transaction, Category
from routes.auth import token_required
from datetime import date

transactions_bp = Blueprint('transactions', __name__)


# ── GET /api/transactions ─────────────────────
@transactions_bp.route('/transactions', methods=['GET'])
@token_required
def get_transactions(current_user):
    # Optional filters from query params: ?type=expense&category_id=2
    type_filter = request.args.get('type')
    category_filter = request.args.get('category_id')

    query = Transaction.query.filter_by(user_id=current_user.id)

    if type_filter:
        query = query.filter_by(type=type_filter)
    if category_filter:
        query = query.filter_by(category_id=category_filter)

    transactions = query.order_by(Transaction.date.desc()).all()
    return jsonify({'transactions': [t.to_dict() for t in transactions]}), 200


# ── POST /api/transactions ────────────────────
@transactions_bp.route('/transactions', methods=['POST'])
@token_required
def add_transaction(current_user):
    data = request.get_json()

    if not data or not data.get('amount') or not data.get('type') or not data.get('date'):
        return jsonify({'error': 'amount, type, and date are required'}), 400

    if data['type'] not in ('income', 'expense'):
        return jsonify({'error': 'type must be income or expense'}), 400

    cat_id = data.get('category_id') or None
    if cat_id == '': cat_id = None

    transaction = Transaction(
        user_id=current_user.id,
        category_id=cat_id,
        amount=data['amount'],
        type=data['type'],
        description=data.get('description', ''),
        date=date.fromisoformat(data['date'])
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        'message': 'Transaction added',
        'transaction': transaction.to_dict()
    }), 201


# ── PUT /api/transactions/<id> ────────────────
@transactions_bp.route('/transactions/<int:transaction_id>', methods=['PUT'])
@token_required
def update_transaction(current_user, transaction_id):
    transaction = Transaction.query.filter_by(
        id=transaction_id, user_id=current_user.id
    ).first()

    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404

    data = request.get_json()
    if 'amount'      in data: transaction.amount      = data['amount']
    if 'type'        in data: transaction.type        = data['type']
    if 'description' in data: transaction.description = data['description']
    if 'date'        in data: transaction.date        = date.fromisoformat(data['date'])
    if 'category_id' in data: transaction.category_id = data['category_id']

    db.session.commit()
    return jsonify({'message': 'Transaction updated', 'transaction': transaction.to_dict()}), 200


# ── DELETE /api/transactions/<id> ─────────────
@transactions_bp.route('/transactions/<int:transaction_id>', methods=['DELETE'])
@token_required
def delete_transaction(current_user, transaction_id):
    transaction = Transaction.query.filter_by(
        id=transaction_id, user_id=current_user.id
    ).first()

    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404

    db.session.delete(transaction)
    db.session.commit()
    return jsonify({'message': 'Transaction deleted'}), 200


# ── GET /api/categories ───────────────────────
@transactions_bp.route('/categories', methods=['GET'])
@token_required
def get_categories(current_user):
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return jsonify({'categories': [c.to_dict() for c in categories]}), 200


# ── POST /api/categories ──────────────────────
@transactions_bp.route('/categories', methods=['POST'])
@token_required
def add_category(current_user):
    data = request.get_json()
    if not data.get('name') or not data.get('type'):
        return jsonify({'error': 'name and type are required'}), 400

    category = Category(
        user_id=current_user.id,
        name=data['name'],
        type=data['type']
    )
    db.session.add(category)
    db.session.commit()
    return jsonify({'message': 'Category added', 'category': category.to_dict()}), 201
