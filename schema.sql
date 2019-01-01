-- PRAGMA foreign_keys = ON;
-- PRAGMA page_size = 65536;
-- PRAGMA cache_size= 100000;



CREATE TABLE IF NOT EXISTS `traces`
(`requestname` TEXT, `timestamp` TEXT);



CREATE TABLE IF NOT EXISTS `file_names`
(`name` TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS `idx_file_names`
ON `file_names`(`name`);



CREATE TABLE IF NOT EXISTS `value_types`
(
    `php_type` TEXT,
    PRIMARY KEY(`php_type`)
);
INSERT OR IGNORE INTO `value_types` (`php_type`) VALUES
('null'),
('boolean'),
('string'),
('integer'),
('double'),
('array'),
('object'),
('unknown'),
('resource');



CREATE TABLE IF NOT EXISTS `values`
(
    `value` TEXT,
    `php_type` INTEGER,

    FOREIGN KEY(`php_type`) REFERENCES `value_types`(`ROWID`)
);
CREATE UNIQUE INDEX IF NOT EXISTS `idx_values`
ON `values`(`value`);



CREATE TABLE IF NOT EXISTS `function_names`
(`name` TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS `idx_function_names`
ON `function_names`(`name`);



CREATE TABLE IF NOT EXISTS `function_invocations`
(
    `hash` TEXT UNIQUE,
    `name` INTEGER,
    `returnval` INTEGER,
    `calling_filename` INTEGER,
    `definition_filename` INTEGER,
    `linenum` INTEGER,
    `memory` INTEGER,
    `time` INTEGER,
    `requestname` TEXT,

    FOREIGN KEY(`name`) REFERENCES `function_names`(`ROWID`),
    FOREIGN KEY(`calling_filename`) REFERENCES `file_names`(`ROWID`),
    FOREIGN KEY(`definition_filename`) REFERENCES `file_names`(`ROWID`),
    FOREIGN KEY(`returnval`) REFERENCES `values`(`ROWID`),
    FOREIGN KEY(`memory`) REFERENCES `values`(`ROWID`),
    FOREIGN KEY(`time`) REFERENCES `values`(`ROWID`),
    FOREIGN KEY(`requestname`) REFERENCES `traces`(`requestname`)
);
CREATE INDEX IF NOT EXISTS `idx_function_invocation_name`
ON `function_invocations`(`name`);


-- each function invocation has an associated set
-- of `n` parameters
CREATE TABLE IF NOT EXISTS `invocation_parameters`
(
    `function_invocation_hash` TEXT,
    `value_id` INTEGER,

    FOREIGN KEY(`function_invocation_hash`) REFERENCES `function_invocations`(`hash`),
    FOREIGN KEY(`value_id`) REFERENCES `values`(`ROWID`)
);
CREATE INDEX IF NOT EXISTS `idx_invocation_parameters_hash`
ON `invocation_parameters`(`function_invocation_hash`);


