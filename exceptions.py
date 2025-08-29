# exceptions.py
class VacationSystemException(Exception):
    """휴가 시스템 기본 예외"""
    pass


class AuthenticationError(VacationSystemException):
    """인증 관련 예외"""
    pass


class AuthorizationError(VacationSystemException):
    """권한 관련 예외"""
    pass


class VacationValidationError(VacationSystemException):
    """휴가 신청 유효성 검사 예외"""
    pass


class UserNotFoundError(VacationSystemException):
    """사용자를 찾을 수 없는 예외"""
    pass
