# models.py (B안 + employee_number)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id               = db.Column(db.Integer, primary_key=True)
    employee_number  = db.Column(db.String(32), unique=True, nullable=False, index=True)  # ← 사번
    username         = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password         = db.Column(db.String(256), nullable=False)
    join_date        = db.Column(db.Date, nullable=False)        # YYYY-MM-DD → date
    part             = db.Column(db.String(50), nullable=False, index=True)
    role             = db.Column(db.String(100), nullable=False) # '파트장','팀장' 등 콤마 가능
    is_temp_password = db.Column(db.Boolean, default=False, nullable=False)

    vacations = db.relationship(
        'Vacation',
        back_populates='applicant_user',
        cascade='all, delete-orphan',
        lazy='selectin',
        foreign_keys='Vacation.applicant_user_id',
    )
    notifications = db.relationship(
        'Notification',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    def __repr__(self):
        return f'<User {self.employee_number} / {self.username}>'

class Vacation(db.Model):
    __tablename__ = 'vacations'
    id                 = db.Column(db.Integer, primary_key=True)

    # 호환용(기존 서비스/데이터 유지)
    applicant          = db.Column(db.String(50), nullable=False, index=True)

    # 정석: FK
    applicant_user_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    applicant_user     = db.relationship('User', back_populates='vacations', foreign_keys=[applicant_user_id])

    vacation_type      = db.Column(db.String(20), nullable=False)         # 'annual','am_half_day','pm_half_day'
    start_date         = db.Column(db.Date, nullable=False, index=True)
    end_date           = db.Column(db.Date, nullable=False, index=True)
    reason             = db.Column(db.Text, nullable=False)
    backup             = db.Column(db.String(50), nullable=False)
    status             = db.Column(db.String(32), nullable=False, index=True)  # 'pending_part_leader', ...

    def __repr__(self):
        return f'<Vacation {self.applicant} - {self.start_date}>'

class Notification(db.Model):
    __tablename__ = 'notifications'
    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    message   = db.Column(db.Text, nullable=False)
    is_read   = db.Column(db.Boolean, default=False, nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = db.relationship('User', back_populates='notifications')

    def __repr__(self):
        return f'<Notification {self.user_id} - {self.message[:20]}>'
