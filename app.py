from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import qrcode
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parkway.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# Database Models (imported from models.py)
from models import User, Booking

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please log in.', 'error')
            return redirect(url_for('login'))

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Sign up successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            return redirect(url_for('profile', user_id=user.id))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')

@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get_or_404(user_id)
    bookings = Booking.query.filter_by(user_id=user.id).all()
    return render_template('profile.html', user=user, bookings=bookings)

@app.route('/book/<int:user_id>', methods=['GET', 'POST'])
def book(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        mall_name = request.form['mall_name']
        slot_time = request.form['slot_time']

        # Generate QR Code
        qr_data = f"User: {user.name}, Mall: {mall_name}, Slot: {slot_time}"
        qr_image = qrcode.make(qr_data)
        qr_path = f'static/qr_codes/{user.id}_{mall_name}_{slot_time}.png'
        os.makedirs(os.path.dirname(qr_path), exist_ok=True)
        qr_image.save(qr_path)

        # Save booking
        new_booking = Booking(user_id=user.id, mall_name=mall_name, slot_time=slot_time, qr_code_path=qr_path)
        db.session.add(new_booking)
        db.session.commit()

        return render_template('qr_code.html', qr_path=qr_path)

    return render_template('book.html', user=user)

@app.route('/settings/<int:user_id>', methods=['GET', 'POST'])
def settings(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        if 'delete_account' in request.form:
            db.session.delete(user)
            db.session.commit()
            flash('Account deleted successfully.', 'success')
            return redirect(url_for('home'))

    return render_template('settings.html', user=user)

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
