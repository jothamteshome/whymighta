CREATE TABLE IF NOT EXISTS games (
    guild_id            BIGINT          NOT NULL,
    game_name           VARCHAR(128)    NOT NULL,
    game_hash           VARCHAR(32)     NOT NULL,
    PRIMARY KEY (guild_id, game_hash),
    CONSTRAINT games_guilds_fk FOREIGN KEY (guild_id) REFERENCES guilds (guild_id) ON DELETE CASCADE ON UPDATE CASCADE
);