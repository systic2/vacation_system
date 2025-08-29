# README.md
# 휴가 관리 시스템 (Vacation Management System)

Flask 기반의 웹 애플리케이션으로 직원들의 휴가 신청 및 승인 프로세스를 관리합니다.

## 주요 기능

### 사용자 기능
- 로그인/로그아웃
- 비밀번호 변경
- 휴가 신청 (연차, 오전/오후 반차)
- 휴가 신청 내역 조회
- 휴가 신청 취소
- 알림 확인

### 관리자 기능
- 사용자 관리 (추가, 수정, 삭제)
- 비밀번호 초기화
- 휴가 승인/반려

### 승인자 기능
- 휴가 신청 승인/반려
- 결재 대기 목록 조회

## 시스템 구조

### 디렉토리 구조
```
vacation_system/
├── app.py                 # 메인 애플리케이션
├── config.py             # 설정 파일
├── models.py             # 데이터베이스 모델
├── constants.py          # 상수 정의
├── exceptions.py         # 예외 클래스
├── requirements.txt      # 패키지 의존성
├── services/            # 비즈니스 로직
│   ├── auth_service.py
│   ├── user_service.py
│   ├── vacation_service.py
│   └── notification_service.py
└── utils/              # 유틸리티
    ├── decorators.py
    ├── validators.py
    └── vacation_calculator.py
```

### 아키텍처 특징

#### 1. 서비스 계층 (Service Layer)
- 비즈니스 로직을 서비스 클래스로 분리
- 각 서비스는 단일 책임 원칙을 따름
- 재사용 가능한 컴포넌트

#### 2. 유효성 검사 (Validation)
- 입력 데이터 검증을 별도 클래스로 분리
- 일관된 검증 로직 적용

#### 3. 데코레이터 패턴
- 인증/인가 로직을 데코레이터로 구현
- 코드 중복 제거 및 관심사 분리

#### 4. 상수 관리
- 하드코딩된 값들을 상수로 관리
- 유지보수성 향상

## 설치 및 실행

1. 가상환경 생성
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 패키지 설치
```bash
pip install -r requirements.txt
```

3. 환경변수 설정 (.env 파일)
```
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///site.db
```

4. 애플리케이션 실행
```bash
python app.py
```

## 데이터베이스 스키마

### User 테이블
- id: 사용자 ID (Primary Key)
- username: 사용자명 (Unique)
- password: 암호화된 비밀번호
- join_date: 입사일
- part: 소속 파트
- role: 역할 (팀장, 파트장, 팀원)
- is_temp_password: 임시 비밀번호 여부

### Vacation 테이블
- id: 휴가신청 ID (Primary Key)
- applicant: 신청자
- vacation_type: 휴가 종류
- start_date: 시작일
- end_date: 종료일
- reason: 신청 사유
- backup: 업무 대행자
- status: 승인 상태

### Notification 테이블
- id: 알림 ID (Primary Key)
- user_id: 사용자 ID (Foreign Key)
- message: 알림 메시지
- is_read: 읽음 여부
- timestamp: 알림 시간

## 주요 개선사항

1. **모듈화**: 기능별로 파일을 분리하여 코드 가독성 향상
2. **서비스 계층**: 비즈니스 로직을 별도 서비스로 분리
3. **예외 처리**: 커스텀 예외 클래스로 에러 처리 개선
4. **유효성 검사**: 입력 검증 로직 표준화
5. **상수 관리**: 하드코딩된 값들을 상수로 관리
6. **데코레이터**: 인증/인가 로직을 재사용 가능하게 구현
7. **설정 관리**: 환경별 설정을 별도 파일로 관리

## 보안 고려사항

- 비밀번호 해싱 (Werkzeug)
- 세션 기반 인증
- CSRF 보호를 위한 Secret Key 사용
- 입력 데이터 유효성 검사
- SQL Injection 방지 (SQLAlchemy ORM)

## 향후 개선 방향

1. JWT 토큰 기반 인증 도입
2. API 엔드포인트 추가 (REST API)
3. 로깅 시스템 구축
4. 테스트 코드 작성
5. 데이터베이스 마이그레이션 관리
6. 캐싱 시스템 도입
7. 이메일 알림 기능