# utils/init_data.py
from werkzeug.security import generate_password_hash
from models import User, db
from datetime import date, timedelta
import random


def init_default_users():
    """애플리케이션 시작 시 초기 사용자들을 생성합니다."""
    
    # 이미 사용자가 있다면 초기화하지 않음
    if User.query.count() > 0:
        print("기존 사용자가 존재합니다. 초기 데이터 생성을 건너뜁니다.")
        return
    
    print("초기 사용자 데이터를 생성합니다...")
    
    # 기본 비밀번호 (실제 운영에서는 더 복잡하게 설정)
    default_password = "password123!"
    temp_password = "a123456!"
    
    # 초기 사용자 데이터
    initial_users = [
        # 팀장 (관리자)
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
    
    # 사용자 생성
    created_count = 0
    for user_data in initial_users:
        try:
            hashed_password = generate_password_hash(user_data['password'])
            
            new_user = User(
                username=user_data['username'],
                password=hashed_password,
                join_date=user_data['join_date'],
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
    """랜덤한 입사일을 생성합니다."""
    today = date.today()
    
    if years_ago > 0:
        # 년 단위로 과거 날짜 생성
        base_date = today.replace(year=today.year - years_ago)
        # 해당 년도에서 랜덤한 날짜 선택
        days_variation = random.randint(-180, 180)  # ±6개월
        join_date = base_date + timedelta(days=days_variation)
    elif months_ago > 0:
        # 월 단위로 과거 날짜 생성
        target_month = today.month - months_ago
        target_year = today.year
        
        while target_month <= 0:
            target_month += 12
            target_year -= 1
        
        try:
            base_date = today.replace(year=target_year, month=target_month)
        except ValueError:
            # 날짜가 해당 월에 존재하지 않는 경우 (예: 2월 30일)
            base_date = today.replace(year=target_year, month=target_month, day=1)
        
        # 해당 월에서 랜덤한 날짜 선택
        days_variation = random.randint(-15, 15)
        join_date = base_date + timedelta(days=days_variation)
    else:
        join_date = today
    
    # 미래 날짜가 되지 않도록 조정
    if join_date > today:
        join_date = today - timedelta(days=random.randint(1, 30))
    
    return join_date.isoformat()


def print_user_info():
    """생성된 사용자 정보를 출력합니다."""
    print("\n" + "="*60)
    print("🔐 초기 사용자 계정 정보")
    print("="*60)
    
    users = User.query.all()
    
    # 역할별로 그룹화
    team_leaders = [u for u in users if '팀장' in u.role]
    part_leaders = [u for u in users if '파트장' in u.role]
    members = [u for u in users if u.role == '팀원']
    
    print("\n📋 팀장 (관리자 권한)")
    print("-" * 40)
    for user in team_leaders:
        password = "password123!" if not user.is_temp_password else "a123456!"
        print(f"Username: {user.username:<20} Password: {password}")
    
    print("\n👔 파트장")
    print("-" * 40)
    for user in part_leaders:
        password = "password123!" if not user.is_temp_password else "a123456!"
        print(f"Username: {user.username:<20} Password: {password} ({user.part})")
    
    print("\n👥 팀원")
    print("-" * 40)
    for user in members:
        password = "password123!" if not user.is_temp_password else "a123456!"
        temp_indicator = " (임시)" if user.is_temp_password else ""
        print(f"Username: {user.username:<20} Password: {password:<15} ({user.part}){temp_indicator}")
    
    print("\n" + "="*60)
    print("💡 임시 비밀번호 사용자는 로그인 후 비밀번호 변경이 필요합니다.")
    print("💡 기본 비밀번호: password123!")
    print("💡 임시 비밀번호: a123456!")
    print("="*60 + "\n")


def reset_database():
    """데이터베이스를 초기화하고 초기 사용자를 다시 생성합니다."""
    print("⚠️  데이터베이스를 초기화합니다...")
    
    # 모든 테이블 데이터 삭제
    try:
        db.session.query(User).delete()
        db.session.query(Vacation).delete()
        db.session.query(Notification).delete()
        db.session.commit()
        print("✅ 기존 데이터가 삭제되었습니다.")
        
        # 초기 사용자 생성
        init_default_users()
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 데이터베이스 초기화 중 오류: {e}")


if __name__ == "__main__":
    # 직접 실행할 때는 데이터베이스 초기화 옵션 제공
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        from app import app
        with app.app_context():
            reset_database()
