# services/vacation_service.py
from datetime import date
from sqlalchemy import or_, and_
from models import User, Vacation, db
from services.notification_service import NotificationService
from utils.vacation_calculator import VacationCalculator


PENDING_STATES = ('pending_part_leader', 'pending_team_leader')
FINAL_STATES = ('approved', 'rejected')


class VacationService:
    def __init__(self):
        self.notification_service = NotificationService()
        self.calculator = VacationCalculator()

    # ----------------------------
    # Create / Cancel
    # ----------------------------
    def apply_vacation(self, username, vacation_data):
        user_info = User.query.filter_by(username=username).first()

        # 입력은 문자열(YYYY-MM-DD) → date 객체로 변환
        start_date = date.fromisoformat(vacation_data['start_date'])
        end_date = date.fromisoformat(vacation_data['end_date'])

        # 과거 날짜 신청 방지 (오늘은 허용)
        if start_date < date.today():
            return {
                'success': False,
                'message': "과거 날짜로는 휴가를 신청할 수 없습니다.",
                'type': 'error'
            }

        # 3개월 경과 여부
        if not self.calculator.can_use_annual_leave(user_info.join_date):
            return {
                'success': False,
                'message': "입사 후 3개월이 지나야 연차를 사용할 수 있습니다.",
                'type': 'error'
            }

        # 기간 중복 체크
        overlap_check = self._check_vacation_overlap(user_info, start_date, end_date)
        if not overlap_check['success']:
            return overlap_check

        # 잔여 연차 체크
        leave_check = self._check_annual_leave_balance(user_info, vacation_data, start_date, end_date)
        if not leave_check['success']:
            return leave_check

        # 결재 상태 결정 (파트장 본인은 팀장 결재로 바로 올림)
        status = 'pending_team_leader' if '파트장' in user_info.role else 'pending_part_leader'

        # 저장: date 타입 + FK(applicant_user_id) 동시 기록
        new_vacation = Vacation(
            applicant=username,                      # 호환 필드
            applicant_user_id=user_info.id,         # FK 사용
            vacation_type=vacation_data['vacation_type'],
            start_date=start_date,
            end_date=end_date,
            reason=vacation_data['reason'],
            backup=vacation_data['backup'],
            status=status
        )
        db.session.add(new_vacation)
        db.session.commit()

        # 알림
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

        if vacation.status in PENDING_STATES:
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

    # ----------------------------
    # Approve / Reject
    # ----------------------------
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

        # 알림
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

        if vacation.status not in PENDING_STATES:
            return {
                'success': False,
                'message': "이미 처리된 결재입니다.",
                'type': 'error'
            }

        vacation.status = 'rejected'
        db.session.commit()

        # 신청자에게 알림
        applicant_user = self._resolve_applicant_user(vacation)
        if applicant_user:
            message = f"휴가 신청({vacation.start_date})이(가) 반려되었습니다."
            self.notification_service.create_notification(applicant_user.id, message)

        return {
            'success': True,
            'message': "결재가 반려되었습니다.",
            'type': 'success'
        }

    # ----------------------------
    # Queries
    # ----------------------------
    def get_user_vacation_history(self, username):
        # username으로 조회(호환). FK를 모두 채우면 applicant_user_id 기준으로 바꿔도 됨.
        return Vacation.query.filter_by(applicant=username).order_by(Vacation.start_date.desc()).all()

    def get_pending_approvals(self, approver_username):
        """파트장은 동일 파트의 pending_part_leader, 팀장은 모든 pending_team_leader."""
        approver_user = User.query.filter_by(username=approver_username).first()
        approval_list = []

        # --- 파트장: 본인 파트 건만 (FK 우선, FK 없는 과거 데이터는 username 조인으로 보완)
        if '파트장' in approver_user.role:
            # FK 있는 건: vacations.applicant_user_id = users.id
            q_fk = (db.session.query(Vacation, User)
                    .join(User, Vacation.applicant_user_id == User.id)
                    .filter(and_(Vacation.status == 'pending_part_leader',
                                 User.part == approver_user.part))
                    .all())
            for v, u in q_fk:
                approval_list.append({'id': v.id, 'applicant': u.username, 'details': v})

            # FK 없는 과거 데이터 보완: username 조인 (applicant_user_id IS NULL)
            q_legacy = (db.session.query(Vacation, User)
                        .join(User, User.username == Vacation.applicant)
                        .filter(and_(Vacation.status == 'pending_part_leader',
                                     Vacation.applicant_user_id.is_(None),
                                     User.part == approver_user.part))
                        .all())
            # 중복 방지(혹시 모를 케이스)
            seen = {item['id'] for item in approval_list}
            for v, u in q_legacy:
                if v.id not in seen:
                    approval_list.append({'id': v.id, 'applicant': u.username, 'details': v})

        # --- 팀장: 모든 pending_team_leader
        if '팀장' in approver_user.role:
            pending_team = Vacation.query.filter_by(status='pending_team_leader').all()
            for v in pending_team:
                approval_list.append({'id': v.id, 'applicant': v.applicant, 'details': v})

        return approval_list

    # ----------------------------
    # Internal helpers
    # ----------------------------
    def _check_vacation_overlap(self, user_info, new_start_date: date, new_end_date: date):
        """동일 사용자의 승인/대기 중인 휴가와 기간 겹침 방지 (date 타입 비교)."""
        existing_vacations = (Vacation.query
                              .filter(or_(Vacation.applicant_user_id == user_info.id,
                                          Vacation.applicant == user_info.username))
                              .all())
        for v in existing_vacations:
            if v.status in PENDING_STATES + ('approved',):
                # v.start_date / v.end_date 는 date 타입
                if not (new_end_date < v.start_date or new_start_date > v.end_date):
                    return {
                        'success': False,
                        'message': "해당 기간에 이미 신청된 휴가가 있습니다.",
                        'type': 'error'
                    }
        return {'success': True}

    def _check_annual_leave_balance(self, user_info, vacation_data, start_date: date, end_date: date):
        total_annual_leave = self.calculator.calculate_annual_leave(user_info.join_date)
        used_annual_leave = self._calculate_used_annual_leave(user_info)

        vtype = vacation_data['vacation_type']
        if vtype == 'annual':
            requested_days = (end_date - start_date).days + 1
        elif vtype in ('am_half_day', 'pm_half_day'):
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

    def _calculate_used_annual_leave(self, user_info):
        """승인되었거나 진행 중인(대기 포함) 연차 소모량 계산."""
        existing_vacations = (Vacation.query
                              .filter(or_(Vacation.applicant_user_id == user_info.id,
                                          Vacation.applicant == user_info.username))
                              .all())
        used_days = 0.0
        for v in existing_vacations:
            if v.status in PENDING_STATES + ('approved',):
                if v.vacation_type == 'annual':
                    used_days += (v.end_date - v.start_date).days + 1
                elif v.vacation_type in ('am_half_day', 'pm_half_day'):
                    used_days += 0.5
        return used_days

    def _send_application_notification(self, user_info, status):
        if status == 'pending_team_leader':
            # 팀장에게 알림
            team_le_
