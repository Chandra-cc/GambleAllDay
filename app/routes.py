from app import app, google, db
from flask import render_template, redirect, url_for, request, session
from app.models import User
import random
import datetime

@app.route('/')
def home():
    if 'google_token' in session:
        user = User.query.filter_by(google_id=session['google_id']).first()
        return render_template('home.html', user=user)
    return redirect(url_for('login'))

@app.route('/login')
def login():
    # Start the Google OAuth process using authorize_redirect
    redirect_uri = url_for('authorized', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/logout')
def logout():
    session.pop('google_token')
    return redirect(url_for('home'))

@app.route('/login/authorized')
def authorized():
    # Handle the OAuth response and access token
    response = google.authorize_access_token()
    if response is None or response.get('access_token') is None:
        return redirect(url_for('home'))

    session['google_token'] = (response['access_token'], '')
    user_info = google.get('userinfo')
    user_data = user_info.data
    user = User.query.filter_by(google_id=user_data['id']).first()

    if user is None:
        user = User(google_id=user_data['id'], name=user_data['name'])
        db.session.add(user)
        db.session.commit()

    session['google_id'] = user_data['id']
    return redirect(url_for('home'))

@app.route('/game')
def game():
    if 'google_token' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(google_id=session['google_id']).first()
    day = (datetime.datetime.now() - user.created_at).days + 1
    number_range = 10 * day
    correct_number = random.randint(1, number_range)
    session['correct_number'] = correct_number
    return render_template('game.html', user=user, day=day, number_range=number_range)

@app.route('/guess', methods=['POST'])
def guess():
    if 'google_token' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(google_id=session['google_id']).first()
    guessed_number = int(request.form['guess'])
    correct_number = session.get('correct_number')

    if guessed_number == correct_number:
        user.coins += 0.1 * (10 * (datetime.datetime.now() - user.created_at).days + 1)
        db.session.commit()

    return redirect(url_for('game'))
