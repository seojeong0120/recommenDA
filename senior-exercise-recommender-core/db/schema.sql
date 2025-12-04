-- Database schema for senior exercise recommender (PostgreSQL)

-- Users table (테이블명 user는 예약어라 users로 변경)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY, -- AUTOINCREMENT 대신 SERIAL 사용
    phone VARCHAR(20) UNIQUE NOT NULL, -- 로그인 ID로 사용
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(50) NOT NULL, -- nickname 대신 name 사용 (코드와 통일)
    birth_date VARCHAR(8),
    gender VARCHAR(10),
    age_group VARCHAR(20), -- "60-64", "65-69" 등
    health_conditions TEXT[], -- PostgreSQL 배열 타입 (JSON 문자열 대신 배열 사용 추천)
    exercise_goals TEXT[],    -- PostgreSQL 배열 타입
    preferred_location VARCHAR(20) DEFAULT 'any',
    guardian_phone VARCHAR(20),
    address_road VARCHAR(255),
    latitude DOUBLE PRECISION, -- REAL 대신 DOUBLE PRECISION
    longitude DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Facilities table (운동 시설 정보 - 코드가 필요로 해서 추가)
CREATE TABLE IF NOT EXISTS facilities (
    id SERIAL PRIMARY KEY,
    fac_id VARCHAR(50) UNIQUE,
    facility_name VARCHAR(100),
    program_name VARCHAR(100),
    sport_category VARCHAR(50),
    address VARCHAR(255),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    is_indoor BOOLEAN
);

-- Group exercise sessions
CREATE TABLE IF NOT EXISTS group_session (
    id SERIAL PRIMARY KEY,
    fac_id VARCHAR(50) NOT NULL,
    fac_name VARCHAR(100) NOT NULL,
    program_name VARCHAR(100) NOT NULL,
    session_date DATE NOT NULL,
    time_block VARCHAR(20) NOT NULL,
    max_participants INTEGER DEFAULT 4,
    current_participants INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fac_id, program_name, session_date, time_block)
);

-- Participants in group sessions
CREATE TABLE IF NOT EXISTS group_participant (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES group_session(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(session_id, user_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_group_session_lookup 
    ON group_session(fac_id, program_name, session_date, time_block);
CREATE INDEX IF NOT EXISTS idx_group_participant_session 
    ON group_participant(session_id);
CREATE INDEX IF NOT EXISTS idx_group_participant_user 
    ON group_participant(user_id);