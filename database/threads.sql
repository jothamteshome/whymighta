CREATE TABLE IF NOT EXISTS `threads` (
  `thread_id`   BIGINT UNSIGNED 	PRIMARY KEY 	COMMENT 'The 64 bit ID representing a thread',
  `guild_id` 	BIGINT UNSIGNED     NOT NULL		COMMENT 'The 64 bit ID representing a guild',
  `user_id` 	BIGINT UNSIGNED 	NOT NULL	    COMMENT 'The 64 bit ID representing a user',
  UNIQUE KEY `one_thread_per_user_per_guild` (`guild_id`, `user_id`),
  FOREIGN KEY (`guild_id`) REFERENCES `guilds` (`guild_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Contains information about threads';