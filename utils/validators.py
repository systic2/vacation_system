# utils/validators.py
import re
from datetime import date


class VacationValidator:
    @staticmethod
    def validate_date_range(start_date_str, end_date_str):
        """날짜 범위의 유효성을 검사합니다."""
        try:
            start_date = date.fromisoformat(start_date_str)
            end_date = date.fromisoformat(end_date_str)
            
            if start_date > end_date:
                return {
                    'valid': False,
                    'message': "시작 날짜가 종료 날짜보다 늦을 수 없습니다."
                }
            
            if start_date < date.today():
                return {
                    'valid': False,
                    'message': "과거 날짜로는 휴가를 신청할 수 없습니다."
                }
            
            return {'valid': True}
            
        except ValueError:
            return {
                'valid': False,
                'message': "올바른 날짜 형식이 아닙니다."
            }
    
    @staticmethod
    def validate_vacation_type(vacation_type):
        """휴가 타입의 유효성을 검사합니다."""
        valid_types = ['annual', 'am_half_day', 'pm_half_day', 'sick', 'special']
        
        if vacation_type not in valid_types:
            return {
                'valid': False,
                'message': "유효하지 않은 휴가 타입입니다."
            }
        
        return {'valid': True}


class PasswordValidator:
    @staticmethod
    def validate_password(password):
        """비밀번호 복잡성을 검사합니다."""
        if len(password) < 8:
            return {
                'valid': False,
                'message': "비밀번호는 최소 8자 이상이어야 합니다."
            }
        
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
