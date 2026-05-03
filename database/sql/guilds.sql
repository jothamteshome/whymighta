CREATE TABLE IF NOT EXISTS guilds (
    guild_id            BIGINT          PRIMARY KEY,
    mock_mode           BOOLEAN         NOT NULL DEFAULT FALSE,
    binary_mode         BOOLEAN         NOT NULL DEFAULT FALSE,
    last_message_sent   TIMESTAMPTZ     NOT NULL DEFAULT '1970-01-01 00:00:00+00',
    bot_channel_id      BIGINT          DEFAULT NULL,
    theme               JSONB           DEFAULT NULL
);