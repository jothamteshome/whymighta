CREATE TABLE IF NOT EXISTS users (
    user_id             BIGINT          PRIMARY KEY,
    global_chat_score   INT             NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_users_global_score ON users (global_chat_score DESC);
