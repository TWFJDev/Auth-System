from flask_sqlalchemy import SQLAlchemy
import datetime
import uuid

db = SQLAlchemy()  # Create a global SQLAlchemy instance
metadata = db.MetaData()

class User(db.Model):
    id = db.Column(db.String(150), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password
