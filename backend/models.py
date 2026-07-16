# pyrefly: ignore [missing-import]
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ──────────────────────────────────────────────
# 1. USERS
# ──────────────────────────────────────────────
class User(db.Model):
    __tablename__ = 'users'

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    categories    = db.relationship('Category',    backref='user', lazy=True)
    transactions  = db.relationship('Transaction', backref='user', lazy=True)
    budgets       = db.relationship('Budget',      backref='user', lazy=True)
    debts         = db.relationship('Debt',        backref='user', lazy=True)
    payoff_plans  = db.relationship('PayoffPlan',  backref='user', lazy=True)

    def to_dict(self):
        return {
            'id':         self.id,
            'name':       self.name,
            'email':      self.email,
            'created_at': self.created_at.isoformat()
        }


# ──────────────────────────────────────────────
# 2. CATEGORIES
# ──────────────────────────────────────────────
class Category(db.Model):
    __tablename__ = 'categories'

    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name    = db.Column(db.String(100), nullable=False)
    type    = db.Column(db.Enum('income', 'expense'), nullable=False)

    transactions = db.relationship('Transaction', backref='category', lazy=True)
    budgets      = db.relationship('Budget',      backref='category', lazy=True)

    def to_dict(self):
        return {
            'id':      self.id,
            'user_id': self.user_id,
            'name':    self.name,
            'type':    self.type
        }


# ──────────────────────────────────────────────
# 3. TRANSACTIONS
# ──────────────────────────────────────────────
class Transaction(db.Model):
    __tablename__ = 'transactions'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    amount      = db.Column(db.Numeric(10, 2), nullable=False)
    type        = db.Column(db.Enum('income', 'expense'), nullable=False)
    description = db.Column(db.String(255))
    date        = db.Column(db.Date, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':           self.id,
            'user_id':      self.user_id,
            'category_id':  self.category_id,
            'category_name': self.category.name if self.category else None,
            'amount':       float(self.amount),
            'type':         self.type,
            'description':  self.description,
            'date':         self.date.isoformat(),
            'created_at':   self.created_at.isoformat()
        }


# ──────────────────────────────────────────────
# 4. BUDGETS
# ──────────────────────────────────────────────
class Budget(db.Model):
    __tablename__ = 'budgets'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id  = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    limit_amount = db.Column(db.Numeric(10, 2), nullable=False)
    month        = db.Column(db.Integer, nullable=False)   # 1–12
    year         = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id':            self.id,
            'user_id':       self.user_id,
            'category_id':   self.category_id,
            'category_name': self.category.name if self.category else None,
            'limit_amount':  float(self.limit_amount),
            'month':         self.month,
            'year':          self.year
        }


# ──────────────────────────────────────────────
# 5. DEBTS
# ──────────────────────────────────────────────
class Debt(db.Model):
    __tablename__ = 'debts'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name          = db.Column(db.String(150), nullable=False)
    principal     = db.Column(db.Numeric(10, 2), nullable=False)
    balance       = db.Column(db.Numeric(10, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)   # annual %
    min_payment   = db.Column(db.Numeric(10, 2), nullable=False)
    due_date      = db.Column(db.Date, nullable=True)

    def to_dict(self):
        return {
            'id':            self.id,
            'user_id':       self.user_id,
            'name':          self.name,
            'principal':     float(self.principal),
            'balance':       float(self.balance),
            'interest_rate': float(self.interest_rate),
            'min_payment':   float(self.min_payment),
            'due_date':      self.due_date.isoformat() if self.due_date else None
        }


# ──────────────────────────────────────────────
# 6. PAYOFF PLANS
# ──────────────────────────────────────────────
class PayoffPlan(db.Model):
    __tablename__ = 'payoff_plans'

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    method          = db.Column(db.Enum('avalanche', 'snowball'), nullable=False)
    extra_payment   = db.Column(db.Numeric(10, 2), default=0)
    months_to_freedom = db.Column(db.Integer)
    total_interest  = db.Column(db.Numeric(10, 2))
    plan_json       = db.Column(db.Text)   # full schedule as JSON string
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':               self.id,
            'user_id':          self.user_id,
            'method':           self.method,
            'extra_payment':    float(self.extra_payment),
            'months_to_freedom': self.months_to_freedom,
            'total_interest':   float(self.total_interest) if self.total_interest else None,
            'plan_json':        self.plan_json,
            'created_at':       self.created_at.isoformat()
        }
