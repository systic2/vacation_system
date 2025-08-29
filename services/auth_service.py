# services/auth_service.py
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, db
import re


class AuthService:
    def authenticate_user(self, username, password):
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            return {
                'success': True,
                'is_temp_password': user.is_temp_password
            }
        else:
            return {
                'success': False,
                'message': "로그인 실패. 아이디 또는 비밀번호가 올바르지 않습니다."
            }
    
    def change_password(self, username, new_password, confirm_password):
        temp_password = "a123456!"
        
        if new_password == temp_password:
            return {
                'success': False,
                'message': "새 비밀번호는 임시 비밀번호와 같을 수 없습니다.",
                'type': 'error'
            }
        
        if new_password != confirm_password:
            return {
                'success': False,
                'message': "새 비밀번호와 확인 비밀번호가 일치하지 않습니다.",
                'type': 'error'
            }
        
        if len(new_password) < 8:
            return {
                'success': False,
                'message': "비밀번호는 최소 8자 이상이어야 합니다.",
                'type': 'error'
            }
        
        validation_result = self._validate_password_complexity(new_password)
        if not validation_result['valid']:
            return {
                'success': False,
                'message': validation_result['message'],
                'type': 'error'
            }
        
        user = User.query.filter_by(username=username).first()
        user.password = generate_password_hash(new_password)
        user.is_temp_password = False
        db.session.commit()
        
        return {
            'success': True,
            'message': "비밀번호가 성공적으로 변경되었습니다.",
            'type': 'success'
        }
    
    def _validate_password_complexity(self, password):
        has_uppercase = bool(re.search(r'[A-Z]', password))
        has_lowercase = bool(re.search(r'[a-z]', password))
        has_number = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*()_+]', password))
        
        criteria_met = sum([has_uppercase, has_lowercase, has_number, has_special])
        
        if criteria_met < 3:
            return {
                'valid': False,
                'message': "비밀번호는 영문 대문자, 소문자, 숫자, 특수문자 중 3가지 이상을 포함해야 합니다."
            }
        
        return {'valid': True}
