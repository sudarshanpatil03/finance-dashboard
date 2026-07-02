from flask import Blueprint, request, jsonify
from models import db, Transaction, Budget, Category
from routes.auth import token_required
# pyrefly: ignore [missing-import]
from sqlalchemy import func
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)


# ── GET /api/dashboard/summary ────────────────
# Optional: ?month=7&year=2025  (defaults to current month)
@dashboard_bp.route('/dashboard/summary', methods=['GET'])
@token_required
def get_summary(current_user):
    now   = datetime.utcnow()
    month = request.args.get('month', now.month, type=int)
    year  = request.args.get('year',  now.year,  type=int)

    uid = current_user.id

    # ── Total Income this month ──
    total_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == uid,
        Transaction.type    == 'income',
        func.month(Transaction.date) == month,
        func.year(Transaction.date)  == year
    ).scalar() or 0

    # ── Total Expenses this month ──
    total_expenses = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == uid,
        Transaction.type    == 'expense',
        func.month(Transaction.date) == month,
        func.year(Transaction.date)  == year
    ).scalar() or 0

    net_savings = float(total_income) - float(total_expenses)

    # ── Spending by Category (for Pie Chart) ──
    category_breakdown = db.session.query(
        Category.name,
        func.sum(Transaction.amount).label('total')
    ).join(Transaction, Transaction.category_id == Category.id)\
     .filter(
        Transaction.user_id == uid,
        Transaction.type    == 'expense',
        func.month(Transaction.date) == month,
        func.year(Transaction.date)  == year
    ).group_by(Category.name).all()

    category_data = [
        {'category': row.name, 'amount': float(row.total)}
        for row in category_breakdown
    ]

    # ── Budget vs Actual (for Bar Chart) ──
    budgets = Budget.query.filter_by(user_id=uid, month=month, year=year).all()
    budget_vs_actual = []
    for b in budgets:
        actual = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id     == uid,
            Transaction.category_id == b.category_id,
            Transaction.type        == 'expense',
            func.month(Transaction.date) == month,
            func.year(Transaction.date)  == year
        ).scalar() or 0

        budget_vs_actual.append({
            'category': b.category.name if b.category else 'Unknown',
            'budget':   float(b.limit_amount),
            'actual':   float(actual)
        })

    # ── Monthly Net Worth Trend (last 6 months, for Line Chart) ──
    trend = []
    for i in range(5, -1, -1):
        # Calculate month offset
        m = month - i
        y = year
        while m <= 0:
            m += 12
            y -= 1

        inc = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == uid,
            Transaction.type    == 'income',
            func.month(Transaction.date) == m,
            func.year(Transaction.date)  == y
        ).scalar() or 0

        exp = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == uid,
            Transaction.type    == 'expense',
            func.month(Transaction.date) == m,
            func.year(Transaction.date)  == y
        ).scalar() or 0

        trend.append({
            'month':      f"{y}-{m:02d}",
            'income':     float(inc),
            'expenses':   float(exp),
            'net':        float(inc) - float(exp)
        })

    # ── Recent Transactions (last 5) ──
    recent = Transaction.query.filter_by(user_id=uid)\
                              .order_by(Transaction.date.desc())\
                              .limit(5).all()

    return jsonify({
        'month':              month,
        'year':               year,
        'total_income':       float(total_income),
        'total_expenses':     float(total_expenses),
        'net_savings':        net_savings,
        'category_breakdown': category_data,
        'budget_vs_actual':   budget_vs_actual,
        'monthly_trend':      trend,
        'recent_transactions': [t.to_dict() for t in recent]
    }), 200
