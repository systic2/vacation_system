# services/user_service.py
from werkzeug.security import generate_password_hash
from models import User, db


class UserService:
    def get_user_by_username(self, username):
        return User.query.filter_by(username=username).first()
    
    def get_user_by_id(self, user_id):
        return User.query.get_or_404(user_id)
    
    def get_all_users(self):
        return User.query.all()
    
    def create_user(self, user_data):
        if User.query.filter_by(username=user_data['username']).first():
            return {
                'success': False,
                'message': "이미 존재하는 사용자 아이디입니다.",
                'type': 'error'
            }
        
        temp_password = "a123456!"
        hashed_password = generate_password_hash(temp_password)
        
        new_user = User(
            username=user_data['username'],
            password=hashed_password,
            join_date=user_data['join_date'],
            part=user_data['part'],
            role=user_data['role'],
            is_temp_password=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return {
            'success': True,
            'message': f"{user_data['username']} 사용자가 성공적으로 추가되었습니다. 임시 비밀번호는 '{temp_password}'입니다.",
            'type': 'success'
        }
    
    def update_user(self, user_id, user_data):
        user = self.get_user_by_id(user_id)
        
        user.username = user_data['username']
        user.join_date = user_data['join_date']
        user.part = user_data['part']
        user.role = user_data['role']
        
        db.session.commit()
        
        return {
            'success': True,
            'message': "사용자 정보가 성공적으로 수정되었습니다.",
            'type': 'success'
        }
    
    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        db.session.delete(user)
        db.session.commit()
        
        return {
            'success': True,
            'message': "사용자가 성공적으로 삭제(퇴사)되었습니다.",
            'type': 'success'
        }
    
    def reset_password(self, user_id):
        user = self.get_user_by_id(user_id)
        temp_password = "a123456!"
        
        user.password = generate_password_hash(temp_password)
        user.is_temp_password = True
        db.session.commit()
        
        return {
            'success': True,
            'message': f"{user.username}의 비밀번호가 '{temp_password}'로 초기화되었습니다. 사용자는 로그인 후 즉시 비밀번호를 변경해야 합니다.",
            'type': 'success'
        }
