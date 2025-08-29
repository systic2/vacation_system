# utils/decorators.py
from functools import wraps
from flask import session, redirect, url_for
from models import User


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get('username')
        if not username:
            return redirect(url_for('login'))
        
        user_info = User.query.filter_by(username=username).first()
        if not user_info or '팀장' not in user_info.role:
            return "관리자 권한이 없습니다.", 403
        
        return f(*args, **kwargs)
    return decorated_function
