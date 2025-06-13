CREATE TABLE IF NOT EXISTS `games` (
  `guild_id` 	  BIGINT UNSIGNED NOT NULL	COMMENT 'The id of the guild this game belongs to',
  `game_name` 	VARCHAR(128) 	  NOT NULL 	COMMENT 'The name of the game',
  `game_hash` 	VARCHAR(32) 	  NOT NULL 	COMMENT 'The hash of the lowercase game name',
  PRIMARY KEY (`guild_id`,`game_hash`),
  CONSTRAINT `games_ibfk_1` FOREIGN KEY (`guild_id`) REFERENCES `guilds` (`guild_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Contains links between guilds and games';