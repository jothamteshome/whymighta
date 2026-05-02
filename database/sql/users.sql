CREATE TABLE IF NOT EXISTS users (
    user_id             BIGINT          NOT NULL,
    guild_id            BIGINT          NOT NULL,
    user_chat_score     INT             NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, guild_id),
    CONSTRAINT users_guilds_fk FOREIGN KEY (guild_id) REFERENCES guilds (guild_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_users_guild_id ON users (guild_id);