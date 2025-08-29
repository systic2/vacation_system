# utils/vacation_calculator.py
from datetime import date


class VacationCalculator:
    @staticmethod
    def calculate_annual_leave(join_date_str):
        """입사일 기준으로 연차 개수를 계산합니다."""
        today = date.today()
        join_date = date.fromisoformat(join_date_str)

        # 입사일 기준 만 1년 미만일 경우
        if (today - join_date).days < 365:
            total_months = (today.year - join_date.year) * 12 + today.month - join_date.month
            if today.day < join_date.day:
                total_months -= 1
            return min(total_months, 12)

        # 만 3년차 이상일 경우 가산 연차 부여
        elif today.year - join_date.year >= 3:
            base_leave = 15
            extra_leave_years = today.year - join_date.year - 3
            additional_leave = extra_leave_years // 2 + 1
            return base_leave + additional_leave
        
        # 입사 만 1년차일 경우
        else:
            return 15
    
    @staticmethod
    def can_use_annual_leave(join_date_str):
        """3개월 미만 근무자의 연차 사용 가능 여부를 확인합니다."""
        today = date.today()
        join_date = date.fromisoformat(join_date_str)
        
        # 3개월 전 날짜 계산
        three_months_ago = today
        if today.month >= 3:
            three_months_ago = three_months_ago.replace(month=today.month - 3)
        else:
            three_months_ago = three_months_ago.replace(
                year=today.year - 1, 
                month=today.month + 9
            )
        
        return join_date <= three_months_ago
