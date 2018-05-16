from yoyo import step


step(
  '''
    CREATE TABLE `record`(
      `record_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      `name`      VARCHAR(127) NOT NULL COMMENT 'logger name',
      `ts`        DATETIME(6) NOT NULL COMMENT 'UTC creation time',
      `level`     TINYINT(2) UNSIGNED NOT NULL COMMENT 'log record level',
      `message`   VARCHAR(255) COMMENT 'log record message',
      `logrec`    JSON COMMENT 'log record',
      PRIMARY KEY (`record_id`),
      INDEX `level_name`(`level`, `name`),
      INDEX `ts`(`ts`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb4
    ROW_FORMAT = COMPRESSED
    KEY_BLOCK_SIZE = 4
  ''',
  '''
    DROP TABLE `record`
  '''
)

