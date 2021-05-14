from flask import Blueprint, render_template, request, flash, redirect
from flask_login.utils import login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask.helpers import url_for
from . import db
from .models import User
from flask_login import login_user, current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            flash('Username or password is wrong!')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=remember)

        return redirect('/')
    else:
        return render_template('login.html');


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
        
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')


        if not username or not email or not password or not confirm_password:
            flash('Please fill in all the fields!')
            return redirect(url_for('auth.register'))
        
        user = User.query.filter_by(username=username).first()

        if user:
            flash('User is already registered!')
            return redirect(url_for('auth.register'))

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email is already registered!')
            return redirect(url_for('auth.register'))

        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='sha256')
        )

        db.session.add(user)
        db.session.commit()

        login_user(user, remember=True)
        return redirect('/')
    else:
        return render_template('register.html');


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))