# utils/init_data.py
from werkzeug.security import generate_password_hash
from models import db, User, Vacation, Notification
from datetime import date, timedelta
import random


def init_default_users():
    """애플리케이션 시작 시 초기 사용자들을 생성합니다. (사번/Date 타입 대응)"""

    # 이미 사용자가 있다면 초기화하지 않음
    if User.query.count() > 0:
        print("기존 사용자가 존재합니다. 초기 데이터 생성을 건너뜁니다.")
        return

    print("초기 사용자 데이터를 생성합니다...")

    # 기본 비밀번호 (실제 운영에서는 더 복잡하게 설정)
    default_password = "password123!"
    temp_password = "a123456!"

    # 초기 사용자 데이터(사번은 아래에서 자동 부여)
    initial_users = [
        # 팀장
        {
            'username': 'admin',
            'password': default_password,
            'join_date': get_random_join_date(years_ago=5),
            'part': 'Management',
            'role': '팀장',
            'is_temp_password': False
        },
        {
            'username': 'team_leader',
            'password': default_password,
            'join_date': get_random_join_date(years_ago=4),
            'part': 'Development',
            'role': '팀장',
            'is_temp_password': False
        },

        # 파트장들
        {
            'username': 'dev_part_leader',
            'password': default_password,
            'join_date': get_random_join_date(years_ago=3),
            'part': 'Development',
            'role': '파트장',
            'is_temp_password': False
        },
        {
            'username': 'design_part_leader',
            'password': default_password,
            'join_date': get_random_join_date(years_ago=3),
            'part': 'Design',
            'role': '파트장',
            'is_temp_password': False
        },
        {
            'username': 'marketing_part_leader',
            'password': default_password,
            'join_date': get_random_join_date(years_ago=2),
            'part': 'Marketing',
            'role': '파트장',
            'is_temp_password': False
        },

        # 개발팀 팀원들
        {
            'username': 'dev_john',
            'password': default_password,
            'join_date': get_random_join_date(years_ago=2),
            'part': 'Development',
            'role': '팀원',
            'is_temp_password': False
        },
        {
            'username': 'dev_sarah',
            'password': default_password,
            'join_date': get_random_join_date(years_ago=1),
            'part': 'Development',
            'role': '팀원',
            'is_temp_password': False
        },
        {
            'username': 'dev_mike',
            'password': temp_password,
            'join_date': get_random_join_date(months_ago=8),
            'part': 'Development',
            'role': '팀원',
            'is_temp_password': True
        },
        {
            'username': 'dev_alice',
            'password': default_password,
            'join_date': get_random_join_date(months_ago=6),
            'part': 'Development',
            'role': '팀원',
            'is_temp_password': False
        },

        # 디자인팀 팀원들
        {
            'username': 'design_emma',
            'password': default_password,
            'join_date': get_random_join_date(years_ago=2),
            'part': 'Design',
            'role': '팀원',
            'is_temp_password': False
        },
        {
            'username': 'design_chris',
            'password': default_password,
            'join_date': get_random_join_date(years_ago=1),
            'part': 'Design',
            'role': '팀원',
            'is_temp_password': False
        },
        {
            'username': 'design_lisa',
            'password': temp_password,
            'join_date': get_random_join_date(months_ago=4),
            'part': 'Design',
            'role': '팀원',
            'is_temp_password': True
        },

        # 마케팅팀 팀원들
        {
            'username': 'marketing_david',
            'password': default_password,
            'join_date': get_random_join_date(years_ago=1),
            'part': 'Marketing',
            'role': '팀원',
            'is_temp_password': False
        },
        {
            'username': 'marketing_jenny',
            'password': default_password,
            'join_date': get_random_join_date(months_ago=9),
            'part': 'Marketing',
            'role': '팀원',
            'is_temp_password': False
        },
        {
            'username': 'marketing_tom',
            'password': temp_password,
            'join_date': get_random_join_date(months_ago=2),
            'part': 'Marketing',
            'role': '팀원',
            'is_temp_password': True
        },

        # 신입 직원들 (3개월 미만)
        {
            'username': 'new_employee1',
            'password': temp_password,
            'join_date': get_random_join_date(months_ago=2),
            'part': 'Development',
            'role': '팀원',
            'is_temp_password': True
        },
        {
            'username': 'new_employee2',
            'password': temp_password,
            'join_date': get_random_join_date(months_ago=1),
            'part': 'Design',
            'role': '팀원',
            'is_temp_password': True
        }
    ]

    # 사번 자동 부여: E000001, E000002, ...
    def gen_empno(n):
        return f"E{n:06d}"

    created_count = 0
    for i, user_data in enumerate(initial_users, start=1):
        try:
            empno = gen_empno(i)
            hashed_password = generate_password_hash(user_data['password'])

            # join_date는 date 객체로 저장 (B안 모델 전제)
            jd = user_data['join_date'] if isinstance(user_data['join_date'], date) else date.fromisoformat(user_data['join_date'])

            new_user = User(
                employee_number=empno,
                username=user_data['username'],
                password=hashed_password,
                join_date=jd,
                part=user_data['part'],
                role=user_data['role'],
                is_temp_password=user_data['is_temp_password']
            )

            db.session.add(new_user)
            created_count += 1

        except Exception as e:
            print(f"사용자 {user_data['username']} 생성 중 오류: {e}")
            continue

    try:
        db.session.commit()
        print(f"✅ {created_count}명의 초기 사용자가 성공적으로 생성되었습니다.")
        print_user_info()

    except Exception as e:
        db.session.rollback()
        print(f"❌ 초기 사용자 생성 중 오류가 발생했습니다: {e}")


def get_random_join_date(years_ago=0, months_ago=0):
    """랜덤한 입사일(date 객체)을 생성합니다."""
    today = date.today()

    if years_ago > 0:
        base_date = today.replace(year=today.year - years_ago)
        days_variation = random.randint(-180, 180)  # ±6개월
        join_date = base_date + timedelta(days=days_variation)
    elif months_ago > 0:
        target_month = today.month - months_ago
        target_year = today.year
        while target_month <= 0:
            target_month += 12
            target_year -= 1
        try:
            base_date = today.replace(year=target_year, month=target_month)
        except ValueError:
            base_date = today.replace(year=target_year, month=target_month, day=1)
        days_variation = random.randint(-15, 15)
        join_date = base_date + timedelta(days=days_variation)
    else:
        join_date = today

    # 미래 날짜가 되지 않도록 조정
    if join_date > today:
        join_date = today - timedelta(days=random.randint(1, 30))

    return join_date  # ← date 객체 반환


def print_user_info():
    """생성된 사용자 정보를 출력합니다."""
    print("\n" + "=" * 60)
    print("🔐 초기 사용자 계정 정보")
    print("=" * 60)

    users = User.query.order_by(User.id.asc()).all()

    # 역할별 그룹화
    team_leaders = [u for u in users if '팀장' in u.role]
    part_leaders = [u for u in users if '파트장' in u.role]
    members = [u for u in users if u.role == '팀원']

    def pw_of(u):
        return "a123456!" if u.is_temp_password else "password123!"

    print("\n📋 팀장 (관리자 권한)")
    print("-" * 40)
    for u in team_leaders:
        print(f"EmpNo: {u.employee_number:<10} Username: {u.username:<20} Password: {pw_of(u)}")

    print("\n👔 파트장")
    print("-" * 40)
    for u in part_leaders:
        print(f"EmpNo: {u.employee_number:<10} Username: {u.username:<20} Password: {pw_of(u)} ({u.part})")

    print("\n👥 팀원")
    print("-" * 40)
    for u in members:
        temp_indicator = " (임시)" if u.is_temp_password else ""
        print(f"EmpNo: {u.employee_number:<10} Username: {u.username:<20} Password: {pw_of(u):<15} ({u.part}){temp_indicator}")

    print("\n" + "=" * 60)
    print("💡 임시 비밀번호 사용자는 로그인 후 비밀번호 변경이 필요합니다.")
    print("💡 기본 비밀번호: password123!")
    print("💡 임시 비밀번호: a123456!")
    print("=" * 60 + "\n")


def reset_database():
    """데이터베이스를 초기화하고 초기 사용자를 다시 생성합니다."""
    print("⚠️  데이터베이스를 초기화합니다...")

    try:
        # 삭제 순서: 자식 → 부모
        db.session.query(Notification).delete()
        db.session.query(Vacation).delete()
        db.session.query(User).delete()
        db.session.commit()
        print("✅ 기존 데이터가 삭제되었습니다.")

        # 초기 사용자 생성
        init_default_users()

    except Exception as e:
        db.session.rollback()
        print(f"❌ 데이터베이스 초기화 중 오류: {e}")


if __name__ == "__main__":
    # 직접 실행: python utils/init_data.py --reset
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        from app import app
        with app.app_context():
            reset_database()
