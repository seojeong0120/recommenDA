-- users 테이블의 모든 데이터 조회
SELECT * FROM users;

-- 최근 가입한 사용자 5명 조회
SELECT id, name, phone, gender, birth_date, created_at 
FROM users 
ORDER BY created_at DESC 
LIMIT 5;

-- 전체 사용자 수 확인
SELECT COUNT(*) as total_users FROM users;

-- 상세 정보 조회 (비밀번호 해시 제외)
SELECT 
    id,
    name,
    birth_date,
    gender,
    health_conditions,
    exercise_goals,
    preferred_location,
    phone,
    guardian_phone,
    address_road,
    latitude,
    longitude,
    created_at
FROM users
ORDER BY created_at DESC;

