from flask import Blueprint, request, jsonify
from models import db, Debt, PayoffPlan
from routes.auth import token_required
import subprocess
import json
import os

debts_bp = Blueprint('debts', __name__)


# ── GET /api/debts ────────────────────────────
@debts_bp.route('/debts', methods=['GET'])
@token_required
def get_debts(current_user):
    debts = Debt.query.filter_by(user_id=current_user.id).all()
    return jsonify({'debts': [d.to_dict() for d in debts]}), 200


# ── POST /api/debts ───────────────────────────
@debts_bp.route('/debts', methods=['POST'])
@token_required
def add_debt(current_user):
    data = request.get_json()

    required = ['name', 'principal', 'balance', 'interest_rate', 'min_payment']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    debt = Debt(
        user_id=current_user.id,
        name=data['name'],
        principal=data['principal'],
        balance=data['balance'],
        interest_rate=data['interest_rate'],
        min_payment=data['min_payment'],
        due_date=data.get('due_date')
    )
    db.session.add(debt)
    db.session.commit()
    return jsonify({'message': 'Debt added', 'debt': debt.to_dict()}), 201


# ── PUT /api/debts/<id> ───────────────────────
@debts_bp.route('/debts/<int:debt_id>', methods=['PUT'])
@token_required
def update_debt(current_user, debt_id):
    debt = Debt.query.filter_by(id=debt_id, user_id=current_user.id).first()
    if not debt:
        return jsonify({'error': 'Debt not found'}), 404

    data = request.get_json()
    if 'name'          in data: debt.name          = data['name']
    if 'balance'       in data: debt.balance       = data['balance']
    if 'interest_rate' in data: debt.interest_rate = data['interest_rate']
    if 'min_payment'   in data: debt.min_payment   = data['min_payment']
    if 'due_date'      in data: debt.due_date      = data['due_date']

    db.session.commit()
    return jsonify({'message': 'Debt updated', 'debt': debt.to_dict()}), 200


# ── DELETE /api/debts/<id> ────────────────────
@debts_bp.route('/debts/<int:debt_id>', methods=['DELETE'])
@token_required
def delete_debt(current_user, debt_id):
    debt = Debt.query.filter_by(id=debt_id, user_id=current_user.id).first()
    if not debt:
        return jsonify({'error': 'Debt not found'}), 404

    db.session.delete(debt)
    db.session.commit()
    return jsonify({'message': 'Debt deleted'}), 200


# ── POST /api/debts/payoff ────────────────────
# Calls the C engine (payoff.exe) and saves result to DB
@debts_bp.route('/debts/payoff', methods=['POST'])
@token_required
def generate_payoff(current_user):
    data = request.get_json()
    method        = data.get('method', 'avalanche')   # 'avalanche' or 'snowball'
    extra_payment = data.get('extra_payment', 0)

    # Fetch user's debts
    debts = Debt.query.filter_by(user_id=current_user.id).all()
    if not debts:
        return jsonify({'error': 'No debts found. Add debts first.'}), 400

    # Build input JSON for the C engine
    debts_data = [
        {
            'name':          d.name,
            'balance':       float(d.balance),
            'interest_rate': float(d.interest_rate),
            'min_payment':   float(d.min_payment)
        }
        for d in debts
    ]
    engine_input = json.dumps({
        'debts':         debts_data,
        'extra_payment': extra_payment,
        'method':        method
    })

    # Path to compiled C engine
    engine_path = os.path.join(os.path.dirname(__file__), '..', '..', 'engine', 'payoff.exe')
    engine_path = os.path.abspath(engine_path)

    try:
        result = subprocess.run(
            [engine_path],
            input=engine_input,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            return jsonify({'error': 'Engine error', 'details': result.stderr}), 500

        plan_data = json.loads(result.stdout)

    except FileNotFoundError:
        return jsonify({'error': 'C engine not found. Please compile payoff.c first.'}), 500
    except json.JSONDecodeError:
        return jsonify({'error': 'Engine returned invalid output'}), 500
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Engine timed out'}), 500

    # Save plan to database
    plan = PayoffPlan(
        user_id=current_user.id,
        method=method,
        extra_payment=extra_payment,
        months_to_freedom=plan_data.get('months_to_freedom'),
        total_interest=plan_data.get('total_interest'),
        plan_json=json.dumps(plan_data)
    )
    db.session.add(plan)
    db.session.commit()

    return jsonify({
        'message': 'Payoff plan generated',
        'plan': plan_data
    }), 200


# ── GET /api/debts/payoff/history ─────────────
@debts_bp.route('/debts/payoff/history', methods=['GET'])
@token_required
def get_payoff_history(current_user):
    plans = PayoffPlan.query.filter_by(user_id=current_user.id)\
                            .order_by(PayoffPlan.created_at.desc()).all()
    return jsonify({'plans': [p.to_dict() for p in plans]}), 200
