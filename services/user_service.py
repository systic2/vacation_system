# services/user_service.py
from datetime import date as _date
from werkzeug.security import generate_password_hash
from models import User, db


class UserService:
    # -------- Helpers --------
    def _parse_date(self, value):
        """YYYY-MM-DD 문자열 또는 date 객체를 받아 date로 반환."""
        if isinstance(value, _date):
            return value
        return _date.fromisoformat(value)  # 형식 오류 시 ValueError 발생 → Flask 핸들러/상위에서 처리 가능

    # -------- Getters --------
    def get_user_by_username(self, username):
        return User.query.filter_by(username=username).first()

    def get_user_by_id(self, user_id):
        return User.query.get_or_404(user_id)

    def get_user_by_employee_number(self, employee_number):
        return User.query.filter_by(employee_number=employee_number).first()

    def get_all_users(self):
        return User.query.order_by(User.id.desc()).all()

    # -------- Mutations --------
    def create_user(self, user_data):
        """
        요구 필드:
          - employee_number (사번, UNIQUE)
          - username (아이디, UNIQUE)
          - join_date (YYYY-MM-DD 또는 date)
          - part, role
        """
        emp_no = user_data.get('employee_number', '').strip()
        username = user_data.get('username', '').strip()

        if not emp_no:
            return {'success': False, 'message': "사번은 필수입니다.", 'type': 'error'}
        if not username:
            return {'success': False, 'message': "사용자 아이디는 필수입니다.", 'type': 'error'}

        # 중복 검사
        if User.query.filter_by(employee_number=emp_no).first():
            return {'success': False, 'message': "이미 존재하는 사번입니다.", 'type': 'error'}
        if User.query.filter_by(username=username).first():
            return {'success': False, 'message': "이미 존재하는 사용자 아이디입니다.", 'type': 'error'}

        # 비밀번호 생성(임시)
        temp_password = "a123456!"
        hashed_password = generate_password_hash(temp_password)

        # join_date 파싱
        try:
            jd = self._parse_date(user_data['join_date'])
        except Exception:
            return {'success': False, 'message': "입사일 형식이 올바르지 않습니다. YYYY-MM-DD로 입력해 주세요.", 'type': 'error'}

        new_user = User(
            employee_number=emp_no,
            username=username,
            password=hashed_password,
            join_date=jd,
            part=user_data.get('part', ''),
            role=user_data.get('role', ''),
            is_temp_password=True,
        )
        db.session.add(new_user)
        db.session.commit()

        return {
            'success': True,
            'message': f"{username} 사용자가 추가되었습니다. 임시 비밀번호는 '{temp_password}'입니다.",
            'type': 'success'
        }

    def update_user(self, user_id, user_data):
        """
        변경 가능 필드:
          - employee_number, username, join_date, part, role
        """
        user = self.get_user_by_id(user_id)

        emp_no = user_data.get('employee_number', '').strip()
        username = user_data.get('username', '').strip()

        if not emp_no:
            return {'success': False, 'message': "사번은 비워둘 수 없습니다.", 'type': 'error'}
        if not username:
            return {'success': False, 'message': "사용자 아이디는 비워둘 수 없습니다.", 'type': 'error'}

        # 중복 검사(본인 제외)
        if User.query.filter(User.id != user_id, User.employee_number == emp_no).first():
            return {'success': False, 'message': "다른 사용자와 사번이 중복됩니다.", 'type': 'error'}
        if User.query.filter(User.id != user_id, User.username == username).first():
            return {'success': False, 'message': "다른 사용자와 아이디가 중복됩니다.", 'type': 'error'}

        # join_date 파싱
        try:
            jd = self._parse_date(user_data['join_date'])
        except Exception:
            return {'success': False, 'message': "입사일 형식이 올바르지 않습니다. YYYY-MM-DD로 입력해 주세요.", 'type': 'error'}

        user.employee_number = emp_no
        user.username = username
        user.join_date = jd
        user.part = user_data.get('part', '')
        user.role = user_data.get('role', '')

        db.session.commit()

        return {'success': True, 'message': "사용자 정보가 성공적으로 수정되었습니다.", 'type': 'success'}

    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        db.session.delete(user)
        db.session.commit()
        return {'success': True, 'message': "사용자가 성공적으로 삭제(퇴사)되었습니다.", 'type': 'success'}

    def reset_password(self, user_id):
        user = self.get_user_by_id(user_id)
        temp_password = "a123456!"
        user.password = generate_password_hash(temp_password)
        user.is_temp_password = True
        db.session.commit()
        return {
            'success': True,
            'message': f"{user.username}의 비밀번호가 '{temp_password}'로 초기화되었습니다. 로그인 후 즉시 변경해야 합니다.",
            'type': 'success'
        }
