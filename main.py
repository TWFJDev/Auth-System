from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from datetime import timedelta
from models import db, User, KeyInfo
from dotenv import load_dotenv
import os

load_dotenv()

app_secret = os.getenv('APP_SECRET')

sqlite_bool = os.getenv('USE_SQLITE')

if sqlite_bool == 'true':
    db_uri_string = 'sqlite:///auth.sqlite'
else:
    db_username = os.getenv("DB_USERNAME")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    db_uri_string = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"

app = Flask(__name__)

app.secret_key = f'{app_secret}'.encode()
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.permanent_session_lifetime = timedelta(minutes=45)

bcrypt = Bcrypt(app)

db.init_app(app)

# Initialize the database before handling any request
@app.before_request
def initialize_database():
    if not hasattr(app, 'db_initialized'):
        try:
            db.create_all()
            app.db_initialized = True
        except Exception as e:
            print(f"Database initialization error: {e}")

@app.route('/')
def home():
    return render_template('index.html', session=session)

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('sign-up'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('sign_up.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['username'] = username
            session.permanent = True
            flash('Successfully logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)