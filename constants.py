# constants.py
class VacationStatus:
    PENDING_PART_LEADER = 'pending_part_leader'
    PENDING_TEAM_LEADER = 'pending_team_leader'
    APPROVED = 'approved'
    REJECTED = 'rejected'


class VacationType:
    ANNUAL = 'annual'
    AM_HALF_DAY = 'am_half_day'
    PM_HALF_DAY = 'pm_half_day'
    SICK = 'sick'
    SPECIAL = 'special'


class UserRole:
    TEAM_LEADER = '팀장'
    PART_LEADER = '파트장'
    MEMBER = '팀원'


class AppConfig:
    TEMP_PASSWORD = "a123456!"
    MIN_WORK_MONTHS_FOR_ANNUAL_LEAVE = 3
    BASE_ANNUAL_LEAVE_DAYS = 15
    MAX_ANNUAL_LEAVE_FIRST_YEAR = 12
