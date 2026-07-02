from flask import Blueprint, request, jsonify
from models import db, Budget, Transaction
from routes.auth import token_required
# pyrefly: ignore [missing-import]
from sqlalchemy import func

budgets_bp = Blueprint('budgets', __name__)


# ── GET /api/budgets ──────────────────────────
# Optional: ?month=7&year=2025
@budgets_bp.route('/budgets', methods=['GET'])
@token_required
def get_budgets(current_user):
    month = request.args.get('month', type=int)
    year  = request.args.get('year',  type=int)

    query = Budget.query.filter_by(user_id=current_user.id)
    if month: query = query.filter_by(month=month)
    if year:  query = query.filter_by(year=year)

    budgets = query.all()

    # For each budget, also calculate actual amount spent this month
    result = []
    for b in budgets:
        actual = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id     == current_user.id,
            Transaction.category_id == b.category_id,
            Transaction.type        == 'expense',
            func.month(Transaction.date) == b.month,
            func.year(Transaction.date)  == b.year
        ).scalar() or 0

        entry = b.to_dict()
        entry['actual_spent'] = float(actual)
        entry['remaining']    = float(b.limit_amount) - float(actual)
        result.append(entry)

    return jsonify({'budgets': result}), 200


# ── POST /api/budgets ─────────────────────────
@budgets_bp.route('/budgets', methods=['POST'])
@token_required
def add_budget(current_user):
    data = request.get_json()

    required = ['category_id', 'limit_amount', 'month', 'year']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    # Check if budget for this category/month/year already exists
    existing = Budget.query.filter_by(
        user_id=current_user.id,
        category_id=data['category_id'],
        month=data['month'],
        year=data['year']
    ).first()

    if existing:
        # Update existing budget instead of creating duplicate
        existing.limit_amount = data['limit_amount']
        db.session.commit()
        return jsonify({'message': 'Budget updated', 'budget': existing.to_dict()}), 200

    budget = Budget(
        user_id=current_user.id,
        category_id=data['category_id'],
        limit_amount=data['limit_amount'],
        month=data['month'],
        year=data['year']
    )
    db.session.add(budget)
    db.session.commit()
    return jsonify({'message': 'Budget created', 'budget': budget.to_dict()}), 201


# ── PUT /api/budgets/<id> ─────────────────────
@budgets_bp.route('/budgets/<int:budget_id>', methods=['PUT'])
@token_required
def update_budget(current_user, budget_id):
    budget = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first()
    if not budget:
        return jsonify({'error': 'Budget not found'}), 404

    data = request.get_json()
    if 'limit_amount' in data: budget.limit_amount = data['limit_amount']
    if 'month'        in data: budget.month        = data['month']
    if 'year'         in data: budget.year         = data['year']

    db.session.commit()
    return jsonify({'message': 'Budget updated', 'budget': budget.to_dict()}), 200


# ── DELETE /api/budgets/<id> ──────────────────
@budgets_bp.route('/budgets/<int:budget_id>', methods=['DELETE'])
@token_required
def delete_budget(current_user, budget_id):
    budget = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first()
    if not budget:
        return jsonify({'error': 'Budget not found'}), 404

    db.session.delete(budget)
    db.session.commit()
    return jsonify({'message': 'Budget deleted'}), 200
