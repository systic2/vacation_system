# services/vacation_service.py
from models import User, Vacation, db
from services.notification_service import NotificationService
from utils.vacation_calculator import VacationCalculator
from datetime import date


class VacationService:
    def __init__(self):
        self.notification_service = NotificationService()
        self.calculator = VacationCalculator()
    
    def apply_vacation(self, username, vacation_data):
        user_info = User.query.filter_by(username=username).first()
        
        # 날짜 변환
        start_date = date.fromisoformat(vacation_data['start_date'])
        end_date = date.fromisoformat(vacation_data['end_date'])
        
        # 과거 날짜 체크
        if start_date < date.today():
            return {
                'success': False,
                'message': "과거 날짜로는 휴가를 신청할 수 없습니다.",
                'type': 'error'
            }
        
        # 3개월 미만 근무자 체크
        if not self.calculator.can_use_annual_leave(user_info.join_date):
            return {
                'success': False,
                'message': "입사 후 3개월이 지나야 연차를 사용할 수 있습니다.",
                'type': 'error'
            }
        
        # 휴가 중복 체크
        overlap_check = self._check_vacation_overlap(username, start_date, end_date)
        if not overlap_check['success']:
            return overlap_check
        
        # 연차 잔여일수 체크
        leave_check = self._check_annual_leave_balance(user_info, vacation_data, start_date, end_date)
        if not leave_check['success']:
            return leave_check
        
        # 결재 상태 결정
        status = 'pending_team_leader' if '파트장' in user_info.role else 'pending_part_leader'
        
        # 휴가 신청 생성
        new_vacation = Vacation(
            applicant=username,
            vacation_type=vacation_data['vacation_type'],
            start_date=vacation_data['start_date'],
            end_date=vacation_data['end_date'],
            reason=vacation_data['reason'],
            backup=vacation_data['backup'],
            status=status
        )
        
        db.session.add(new_vacation)
        db.session.commit()
        
        # 알림 발송
        self._send_application_notification(user_info, status)
        
        return {
            'success': True,
            'message': "휴가 신청이 완료되었습니다. 결재 대기 중입니다.",
            'type': 'success'
        }
    
    def cancel_vacation(self, vacation_id, username):
        vacation = Vacation.query.get_or_404(vacation_id)
        
        if vacation.applicant != username:
            return {
                'success': False,
                'message': "자신이 신청한 휴가만 취소할 수 있습니다.",
                'type': 'error'
            }
        
        if vacation.status in ['pending_part_leader', 'pending_team_leader']:
            db.session.delete(vacation)
            db.session.commit()
            return {
                'success': True,
                'message': "휴가 신청이 취소되었습니다.",
                'type': 'success'
            }
        else:
            return {
                'success': False,
                'message': "이미 승인/반려된 휴가는 취소할 수 없습니다.",
                'type': 'error'
            }
    
    def approve_vacation(self, vacation_id, approver_username):
        approver_user = User.query.filter_by(username=approver_username).first()
        vacation = Vacation.query.get_or_404(vacation_id)
        
        current_status = vacation.status
        
        if '팀장' in approver_user.role and current_status == 'pending_team_leader':
            new_status = 'approved'
        elif '파트장' in approver_user.role and current_status == 'pending_part_leader':
            new_status = 'pending_team_leader'
        else:
            return {
                'success': False,
                'message': "잘못된 접근입니다.",
                'type': 'error'
            }
        
        vacation.status = new_status
        db.session.commit()
        
        # 알림 발송
        self._send_approval_notification(vacation, new_status)
        
        return {
            'success': True,
            'message': "결재가 승인되었습니다.",
            'type': 'success'
        }
    
    def reject_vacation(self, vacation_id, approver_username):
        approver_user = User.query.filter_by(username=approver_username).first()
        vacation = Vacation.query.get_or_404(vacation_id)
        
        if '파트장' not in approver_user.role and '팀장' not in approver_user.role:
            return {
                'success': False,
                'message': "결재 권한이 없습니다.",
                'type': 'error'
            }
        
        if vacation.status not in ['pending_part_leader', 'pending_team_leader']:
            return {
                'success': False,
                'message': "이미 처리된 결재입니다.",
                'type': 'error'
            }
        
        vacation.status = 'rejected'
        db.session.commit()
        
        # 신청자에게 알림
        applicant_user = User.query.filter_by(username=vacation.applicant).first()
        message = f"휴가 신청({vacation.start_date})이(가) 반려되었습니다."
        self.notification_service.create_notification(applicant_user.id, message)
        
        return {
            'success': True,
            'message': "결재가 반려되었습니다.",
            'type': 'success'
        }
    
    def get_user_vacation_history(self, username):
        return Vacation.query.filter_by(applicant=username).order_by(Vacation.start_date.desc()).all()
    
    def get_pending_approvals(self, approver_username):
        approver_user = User.query.filter_by(username=approver_username).first()
        approval_list = []
        
        if '파트장' in approver_user.role:
            pending_list = Vacation.query.filter_by(status='pending_part_leader').all()
            for vacation in pending_list:
                applicant_user = User.query.filter_by(username=vacation.applicant).first()
                if applicant_user and applicant_user.part == approver_user.part:
                    approval_list.append({
                        'id': vacation.id,
                        'applicant': vacation.applicant,
                        'details': vacation
                    })

        if '팀장' in approver_user.role:
            pending_list = Vacation.query.filter_by(status='pending_team_leader').all()
            for vacation in pending_list:
                approval_list.append({
                    'id': vacation.id,
                    'applicant': vacation.applicant,
                    'details': vacation
                })

        return approval_list
    
    def _check_vacation_overlap(self, username, new_start_date, new_end_date):
        existing_vacations = Vacation.query.filter_by(applicant=username).all()
        
        for vacation in existing_vacations:
            if vacation.status in ['pending_part_leader', 'pending_team_leader', 'approved']:
                existing_start = date.fromisoformat(vacation.start_date)
                existing_end = date.fromisoformat(vacation.end_date)
                
                if not (new_end_date < existing_start or new_start_date > existing_end):
                    return {
                        'success': False,
                        'message': "해당 기간에 이미 신청된 휴가가 있습니다.",
                        'type': 'error'
                    }
        
        return {'success': True}
    
    def _check_annual_leave_balance(self, user_info, vacation_data, start_date, end_date):
        total_annual_leave = self.calculator.calculate_annual_leave(user_info.join_date)
        used_annual_leave = self._calculate_used_annual_leave(user_info.username)
        
        if vacation_data['vacation_type'] == 'annual':
            requested_days = (end_date - start_date).days + 1
        elif vacation_data['vacation_type'] in ['am_half_day', 'pm_half_day']:
            requested_days = 0.5
        else:
            requested_days = 0
        
        if used_annual_leave + requested_days > total_annual_leave:
            remaining = total_annual_leave - used_annual_leave
            return {
                'success': False,
                'message': f"연차 신청 가능 일수를 초과했습니다. 현재 신청 가능한 잔여 연차: {remaining}일",
                'type': 'error'
            }
        
        return {'success': True}
    
    def _calculate_used_annual_leave(self, username):
        existing_vacations = Vacation.query.filter_by(applicant=username).all()
        used_days = 0
        
        for vacation in existing_vacations:
            if vacation.status in ['approved', 'pending_part_leader', 'pending_team_leader']:
                if vacation.vacation_type == 'annual':
                    start = date.fromisoformat(vacation.start_date)
                    end = date.fromisoformat(vacation.end_date)
                    used_days += (end - start).days + 1
                elif vacation.vacation_type in ['am_half_day', 'pm_half_day']:
                    used_days += 0.5
        
        return used_days
    
    def _send_application_notification(self, user_info, status):
        if status == 'pending_team_leader':
            # 팀장에게 알림
            team_leaders = User.query.filter(User.role.like('%팀장%')).all()
            for team_leader in team_leaders:
                message = f"{user_info.username}님의 휴가 신청이 도착했습니다."
                self.notification_service.create_notification(team_leader.id, message)
        else:
            # 파트장에게 알림
            part_leader = User.query.filter_by(part=user_info.part).filter(
                User.role.like('%파트장%')
            ).first()
            if part_leader:
                message = f"{user_info.username}님의 휴가 신청이 도착했습니다."
                self.notification_service.create_notification(part_leader.id, message)
    
    def _send_approval_notification(self, vacation, new_status):
        if new_status == 'pending_team_leader':
            # 팀장에게 알림
            team_leaders = User.query.filter(User.role.like('%팀장%')).all()
            for team_leader in team_leaders:
                message = f"{vacation.applicant}님의 휴가 신청이 파트장 승인을 완료했습니다."
                self.notification_service.create_notification(team_leader.id, message)
        elif new_status == 'approved':
            # 신청자에게 알림
            applicant_user = User.query.filter_by(username=vacation.applicant).first()
            message = f"휴가 신청({vacation.start_date})이(가) 최종 승인되었습니다."
            self.notification_service.create_notification(applicant_user.id, message)
