from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import random
import os
import pymysql

app = Flask(__name__)

app.secret_key = 'a_super_secret_key_12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://myuser:mypassword@localhost/users_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_NAME'] = 'my_flask_cookie'  # Change session cookie name

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    coins = db.Column(db.Float, default=0.0)
    
    # Track if the user has already guessed today
    has_guessed_today = db.Column(db.Boolean, default=False)  # Add this field
    correct_number = db.Column(db.Integer, nullable=True)
    last_guess_date = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

# Ensure tables are created when app starts
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    print(f"DEBUG: Current Session Data - {session}")  # Debugging line
    
    if 'user_id' not in session:
        # flash("You are logged out. Please log in.", "warning")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if user:
        print(f"DEBUG: Showing home page for {user.email}")  # Debugging line
        return render_template('home.html', user=user)

    flash("User not found. Please log in again.", "error")
    session.pop('user_id', None)  # Remove invalid session
    return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form['password_confirm']

        # Check if passwords match
        if password != password_confirm:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))

        # Create new user and set hashed password
        new_user = User(username=username, email=email)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()  # 🔴 Ensure this line is present
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()  # 🔴 Rollback in case of failure
            flash(f"Database Error: {e}", "error")

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id  # 🔴 Store user ID in session
            flash('Login successful!', 'success')

            print(f"DEBUG: Logged in user - {user.email}")  # Debugging line

            return redirect(url_for('home'))
        else:
            flash('Invalid credentials, please try again.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    print(f"DEBUG: Logging out user {session.get('user_id')}")  # Debugging
    session.pop('user_id', None)  # Clear session
    # flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/game')
def game():
    if 'user_id' not in session:
        flash("Please log in to play.", "warning")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if user.has_guessed_today:
        flash("You have already guessed today. Your earnings: {0} coins.".format(user.coins), "info")
        # return redirect(url_for('home'))
    
    # Calculate the day and number range
    days_played = (datetime.now(timezone.utc).date() - user.created_at.date()).days + 1
    number_range = 10 * days_played  # Increase range every day

    last_guess_date = user.last_guess_date if user.last_guess_date else datetime.now(timezone.utc)
    print(last_guess_date)
    # Reset correct_number if it's a new day
    if user.correct_number is None or last_guess_date.date() < datetime.now(timezone.utc).date():
        user.correct_number = random.randint(1, number_range)
        user.has_guessed_today = False  # Allow guessing again
        user.last_guess_date = datetime.now(timezone.utc)  # Update last played date
        db.session.commit()


    return render_template('game.html', user=user, days_played=days_played, number_range=number_range)


@app.route('/guess', methods=['POST'])
def guess():
    if 'user_id' not in session:
        flash("Please log in to make a guess.", "warning")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if user.has_guessed_today:
        flash("You have already guessed today. Please wait until tomorrow to make a new guess.", "info")
        return redirect(url_for('game'))
    

    user.has_guessed_today = True
    days_played = (datetime.utcnow() - user.created_at).days + 1
    correct_number = user.correct_number 
    guessed_number = int(request.form['guess'])
    flash(f"Correct number was {correct_number} and you guesed {guessed_number}.")
    if guessed_number == correct_number:
        winnings = 0.1 * days_played  # Reward user based on days played
        user.coins += winnings
        db.session.commit()  # Save changes to database
        flash(f"🎉 Correct! You won {winnings} coins! Again try tomorrow!!", "success")
    else:
        flash("❌ Incorrect guess. Try again tomorrow!", "error")
    db.session.commit()

    return redirect(url_for('game'))



if __name__ == '__main__':
    app.run(debug=True)
