# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    join_date = db.Column(db.String(10), nullable=False)
    part = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_temp_password = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'


class Vacation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    applicant = db.Column(db.String(20), nullable=False)
    vacation_type = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.String(10), nullable=False)
    end_date = db.Column(db.String(10), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    backup = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<Vacation {self.applicant} - {self.start_date}>'


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(256), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications')

    def __repr__(self):
        return f'<Notification {self.user_id} - {self.message[:20]}>'
