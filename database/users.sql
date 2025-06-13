CREATE TABLE IF NOT EXISTS `users` (
  `user_id` 		    BIGINT UNSIGNED NOT NULL	COMMENT 'The 64 bit ID representing a user',
  `guild_id` 		    BIGINT UNSIGNED NOT NULL	COMMENT 'The 64 bit ID representing a guild',
  `user_chat_score` INT UNSIGNED 	  NOT NULL	COMMENT 'The value based on the number of messages a user has sent in a guild',
  PRIMARY KEY (`user_id`,`guild_id`),
  KEY `users_guilds_guild_id_fk` (`guild_id`),
  CONSTRAINT `users_guilds_guild_id_fk` FOREIGN KEY (`guild_id`) REFERENCES `guilds` (`guild_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Contains information users belonging to certain guilds';