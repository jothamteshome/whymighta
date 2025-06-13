CREATE TABLE IF NOT EXISTS `guilds` (
  `guild_id` 			      BIGINT UNSIGNED 	PRIMARY KEY 									                  COMMENT 'The 64 bit ID representing a guild',
  `mock` 				        TINYINT 			    NOT NULL DEFAULT 0								              COMMENT 'A boolean value denoting if bot will mock users',
  `binary` 				      TINYINT 			    NOT NULL DEFAULT 0								              COMMENT 'A boolean value denoting if bot will convert messages to binary',
  `last_message_sent` 	DATETIME(6) 		  NOT NULL DEFAULT '1970-01-01 00:00:00.000000'	  COMMENT 'The timestamp of the latest message in the guild was sent',
  `bot_channel_id` 		  BIGINT UNSIGNED 	DEFAULT NULL									                  COMMENT 'The 64 bit ID representing a channel for the bot to send messages in'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Contains information about guilds';