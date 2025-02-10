from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, jsonify
from flask_bcrypt import Bcrypt
from datetime import timedelta
from models import db, User, metadata
from dotenv import load_dotenv
from flask_session import Session
import os, datetime
from sqlalchemy import Column, Integer, String, Table, MetaData, select
from flask_cors import CORS

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
CORS(app)

os.environ['WERKZEUG_SERVER_HEADER'] = 'None'

app.secret_key = f'{app_secret}'.encode()
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'session:'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db.init_app(app)
app.config['SESSION_SQLALCHEMY'] = db
Session(app)

app.permanent_session_lifetime = timedelta(minutes=45)

bcrypt = Bcrypt(app)

@app.before_request
def initialize_database():
    if not hasattr(app, 'db_initialized'):
        try:
            with app.app_context():
                db.create_all()
            app.db_initialized = True
        except Exception as e:
            print(f"Database initialization error: {e}")

@app.route('/')
def home():
    return render_template('index.html', session=session)

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if 'username' in session:
        return redirect(url_for('home'))
    else:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            if User.query.filter_by(username=username).first():
                flash('Username already exists. Please choose a different one.', 'danger')
                return redirect(url_for('sign_up'))

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))

        return render_template('sign_up.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    else:
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
    session.clear()
    flash('You have been logged out.', 'info')
    response = make_response(redirect(url_for('home')))
    session_cookie_name = app.config.get('SESSION_COOKIE_NAME', 'session')
    response.delete_cookie(session_cookie_name)

    return response

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')

def query_table_for_datatables(table_name, start=0, length=10):
    metadata = MetaData()
    metadata.reflect(bind=db.engine)

    table = metadata.tables.get(table_name)
    if table is None:
        return {"error": f"Table '{table_name}' does not exist."}

    stmt = select(table).offset(start).limit(length)
    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        rows = [dict(row) for row in result]

    total_records = db.session.execute(select([table.count()])).scalar() or 0

    return {
        "draw": request.args.get("draw", type=int, default=1),
        "recordsTotal": total_records,
        "recordsFiltered": total_records,
        "data": rows
    }

@app.route('/app/<app_name>')
def app_name(app_name):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', app_name=app_name)

@app.route('/data/<app_name>')
def get_data(app_name):
    metadata = MetaData()
    metadata.reflect(bind=db.engine)

    if app_name not in metadata.tables:
        return jsonify({
            "draw": request.args.get("draw", type=int, default=1),
            "recordsTotal": 0,
            "recordsFiltered": 0,
            "data": []
        })

    table = metadata.tables[app_name]
    stmt = select(table)
    
    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        rows = [dict(row) for row in result]

    total_records = len(rows)

    return jsonify({
        "draw": request.args.get("draw", type=int, default=1),
        "recordsTotal": total_records,
        "recordsFiltered": total_records,
        "data": rows
    })

def create_table(table_name: str):
    new_table = Table(
        table_name, metadata,
        Column('key', String(150), primary_key=True),
        Column('duration', String(150)),
        Column('key_redeemed_time_epoch', String(150)),
        Column('key_end_time_epoch', String(150)),
        Column('status', String(150)),
        Column('created_at', String(150), default=lambda: datetime.datetime.now())
    )
    
    metadata.create_all(db.engine)

    return f"Table '{table_name}' created successfully."

@app.route('/create_app', methods=['POST'])
def create_dynamic_table():
    app_name = request.form.get('app_name')
    if app_name:
        message = create_table(app_name.replace(" ", "_"))
        flash(f"App '{app_name.replace('_', ' ').title()}' created successfully!", "success")
    else:
        flash("Please enter a valid app name.", "danger")
    return redirect(url_for('apps'))

@app.route('/app')
def apps():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    metadata = MetaData()
    metadata.reflect(bind=db.engine)

    table_names = [table for table in metadata.tables.keys() if table not in ('sessions', 'user')]
    
    return render_template('app.html', tables=table_names)

@app.route('/delete_app', methods=['POST'])
def delete_app():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    table_name = request.form.get("table_name")
    
    if not table_name:
        flash("Invalid table name.", "danger")
        return redirect(url_for("apps"))

    metadata = MetaData()
    metadata.reflect(bind=db.engine)

    if table_name in metadata.tables:
        table = metadata.tables[table_name]
        table.drop(db.engine)  # Drop the table from the database
        flash(f"Table '{table_name.replace('_', ' ').title()}' deleted successfully!", "success")
    else:
        flash("Table not found.", "danger")

    return redirect(url_for("apps"))

if __name__ == '__main__':
    app.run(debug=True)