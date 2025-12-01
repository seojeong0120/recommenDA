-- Database schema for senior exercise recommender

-- Users table
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname TEXT NOT NULL,
    age_group TEXT NOT NULL,  -- "60-64", "65-69", "70-74", "75+"
    health_issues TEXT,  -- JSON array string like '["knee_pain", "hypertension"]'
    goals TEXT,  -- JSON array string like '["weight", "blood_pressure"]'
    preference_env TEXT DEFAULT "any",  -- "indoor", "outdoor", "any"
    home_lat REAL,
    home_lon REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Group exercise sessions
CREATE TABLE IF NOT EXISTS group_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fac_id TEXT NOT NULL,
    fac_name TEXT NOT NULL,
    program_name TEXT NOT NULL,
    session_date DATE NOT NULL,  -- YYYY-MM-DD
    time_block TEXT NOT NULL,  -- "오전", "오후", "저녁" 등
    max_participants INTEGER DEFAULT 4,
    current_participants INTEGER DEFAULT 0,
    status TEXT DEFAULT "open",  -- "open", "filled", "completed"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fac_id, program_name, session_date, time_block)
);

-- Participants in group sessions
CREATE TABLE IF NOT EXISTS group_participant (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES group_session(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    UNIQUE(session_id, user_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_group_session_lookup 
    ON group_session(fac_id, program_name, session_date, time_block);
CREATE INDEX IF NOT EXISTS idx_group_participant_session 
    ON group_participant(session_id);
CREATE INDEX IF NOT EXISTS idx_group_participant_user 
    ON group_participant(user_id);

