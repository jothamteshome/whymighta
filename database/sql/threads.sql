CREATE TABLE IF NOT EXISTS threads (
    thread_id           BIGINT          PRIMARY KEY,
    guild_id            BIGINT          NOT NULL,
    user_id             BIGINT          NOT NULL,
    UNIQUE (guild_id, user_id),
    FOREIGN KEY (guild_id) REFERENCES guilds (guild_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id, guild_id) REFERENCES users (user_id, guild_id) ON DELETE CASCADE ON UPDATE CASCADE
);