from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Business, Invoice, InvoiceItem, Payment, TransactionLog
from security import encrypt_data, decrypt_data, hash_data, generate_key
import os
import random

app = Blueprint('main', __name__)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        business_name = request.form['business_name']
        
        business = Business.query.filter_by(name=business_name).first()
        if not business:
            business = Business(name=business_name)
            db.session.add(business)
            db.session.commit()

        new_user = User(username=username, password_hash=hash_data(password), business_id=business.id)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can log in now.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password_hash == hash_data(password):
            # Generate and send 2FA code
            # user.two_factor_code = str(random.randint(100000, 999999))
            user.two_factor_code = str(123456)
            db.session.commit()
            flash(f'Your 2FA code is: {user.two_factor_code}', 'info')
            print("user code",user.two_factor_code)
            return redirect(url_for('main.two_factor_auth', user_id=user.id))
        else:
            flash('Login Unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    invoices = Invoice.query.filter_by(business_id=current_user.business_id).all()
    return render_template('dashboard.html', invoices=invoices)

@app.route('/two_factor_auth/<int:user_id>', methods=['GET', 'POST'])
def two_factor_auth(user_id):
    if request.method == 'POST':
        code = request.form['code']
        user = User.query.get(user_id)
        if user.two_factor_code == code:
            login_user(user)
            user.two_factor_code = None  # Clear the code after successful login
            log_transaction("User logged in", user.id)
            return redirect(url_for('main.dashboard')) 
        else:
            flash('Invalid 2FA code.', 'danger')
    return render_template('two_factor_auth.html', user_id=user_id)

@app.route('/create_invoice', methods=['GET', 'POST'])
@login_required
def create_invoice():
    if request.method == 'POST':
        tax_rate = request.form.get('tax_rate', type=float) or 0.0
        total_amount = 0.0

        # Create a new invoice
        new_invoice = Invoice(business_id=current_user.business_id, tax_rate=tax_rate, status='Pending')
        db.session.add(new_invoice)

        # Iterate over each item and create InvoiceItem records
        for i in range(len(request.form.getlist('description'))):
            description = request.form.getlist('description')[i]
            quantity = int(request.form.getlist('quantity')[i])
            unit_price = int(request.form.getlist('unit_price')[i])

            invoice_item = InvoiceItem(
                invoice=new_invoice,
                description=description,
                quantity=quantity,
                unit_price=unit_price
            )
            invoice_item.calculate_total_price()  # Calculate total price
            total_amount += invoice_item.total_price  # Accumulate total amount

            db.session.add(invoice_item)

        # Update total amount for the invoice
        new_invoice.total_amount = total_amount * (1 + tax_rate / 100)  # Apply tax
        db.session.commit()

        log_transaction("Invoice created", current_user.id)
        flash('Invoice created successfully!', 'success')
        return redirect(url_for('main.dashboard')) 
    return render_template('create_invoice.html')

@app.route('/view_payments/<int:invoice_id>')
@login_required
def view_payments(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    payments = Payment.query.filter_by(invoice_id=invoice_id).all()
    return render_template('view_payments.html', invoice=invoice, payments=payments)

@app.route('/pay_invoice/<int:invoice_id>', methods=['GET', 'POST'])
@login_required
def pay_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    if request.method == 'POST':
        try:
            payment_amount = float(request.form['payment_amount'])
        except ValueError:
            flash('Invalid payment amount.', 'danger')
            return render_template('pay_invoice.html', invoice=invoice)
        
        payment_method = request.form.get('payment_method')
        
        if not payment_method:
            flash('Payment method is required.', 'danger')
            return render_template('pay_invoice.html', invoice=invoice)
        
        # Process the payment
        new_payment = Payment(invoice_id=invoice_id, amount=payment_amount, payment_method=payment_method)
        db.session.add(new_payment)
        
        # Update invoice status if fully paid
        total_paid = sum(payment.amount for payment in Payment.query.filter_by(invoice_id=invoice_id).all())
        if total_paid + payment_amount >= invoice.total_amount:
            invoice.status = 'Fully Paid'
        
        db.session.commit()
        log_transaction("Payment processed", current_user.id)
        flash('Payment processed successfully!', 'success')
        return redirect(url_for('main.view_payments', invoice_id=invoice_id))

    return render_template('pay_invoice.html', invoice=invoice)


@app.route('/view_invoices')
@login_required
def view_invoices():
    invoices = Invoice.query.filter_by(business_id=current_user.business_id).all()
    return render_template('view_invoices.html', invoices=invoices)

@app.route('/view_invoice/<int:invoice_id>', methods=['GET'])
@login_required
def view_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    payments = Payment.query.filter_by(invoice_id=invoice_id).all()
    
    # Decrypt the invoice data
    # decrypted_data = decrypt_data(invoice.encrypted_data, generate_key())
    return render_template('view_invoice_detail.html', invoice=invoice, payments=payments)

@app.route('/approve_invoice/<int:invoice_id>', methods=['POST'])
@login_required
def approve_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    if invoice.business_id == current_user.business_id:
        invoice.approve()
        log_transaction("Invoice approved", current_user.id)
        flash('Invoice approved successfully!', 'success')
    else:
        flash('You do not have permission to approve this invoice.', 'danger')
    return redirect(url_for('main.view_invoices'))

@app.route('/')
def landing_page():
    return render_template('landing.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

def log_transaction(action, user_id):
    log_entry = TransactionLog(action=action, user_id=user_id)
    db.session.add(log_entry)
    db.session.commit()
