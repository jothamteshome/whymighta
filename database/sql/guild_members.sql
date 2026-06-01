CREATE TABLE IF NOT EXISTS guild_members (
    user_id             BIGINT          NOT NULL,
    guild_id            BIGINT          NOT NULL,
    guild_chat_score    INT             NOT NULL DEFAULT 0,
    active              BOOLEAN         NOT NULL DEFAULT TRUE,
    PRIMARY KEY (user_id, guild_id),
    CONSTRAINT gm_users_fk  FOREIGN KEY (user_id)  REFERENCES users  (user_id),
    CONSTRAINT gm_guilds_fk FOREIGN KEY (guild_id) REFERENCES guilds (guild_id)
);

CREATE INDEX IF NOT EXISTS idx_guild_members_guild_id    ON guild_members (guild_id);
CREATE INDEX IF NOT EXISTS idx_guild_members_guild_score ON guild_members (guild_id, guild_chat_score DESC);
