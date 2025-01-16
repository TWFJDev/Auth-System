from flask_sqlalchemy import SQLAlchemy
import datetime
import uuid

db = SQLAlchemy()  # Create a global SQLAlchemy instance

class User(db.Model):
    id = db.Column(db.String(150), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class KeyInfo(db.Model):
    key = db.Column(db.String(150), primary_key=True)
    duration = db.Column(db.String(150))
    key_redeemed_time_epoch = db.Column(db.String(150))
    key_end_time_epoch = db.Column(db.String(150))
    status = db.Column(db.String(150))
    created_at = db.Column(db.String(150), default=lambda: datetime.datetime.now())

    def __init__(self, key, duration, key_redeemed_time_epoch, key_end_time_epoch, status):
        self.key = key
        self.duration = duration
        self.key_redeemed_time_epoch = key_redeemed_time_epoch
        self.key_end_time_epoch = key_end_time_epoch
        self.status = status
