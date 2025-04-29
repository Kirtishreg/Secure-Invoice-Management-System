from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Business(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    users = db.relationship('User', backref='business', lazy=True)
    invoices = db.relationship('Invoice', backref='business', lazy=True)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'))
    two_factor_code = db.Column(db.String(6))  # For MFA

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'))
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True)
    total_amount = db.Column(db.Float, nullable=False)
    tax_rate = db.Column(db.Float, default=0.0)  # Optional tax rate
    status = db.Column(db.String(20), default='Pending')
    
    def approve(self):
        self.status = 'Approved'
        db.session.commit()

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    def calculate_total_price(self):
        self.total_price = self.quantity * self.unit_price


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'))
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    payment_method = db.Column(db.String(50))


class TransactionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
