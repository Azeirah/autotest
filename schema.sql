PRAGMA foreign_keys = ON;
-- PRAGMA page_size = 65536;
-- PRAGMA cache_size= 100000;

CREATE TABLE `function_invocations`
(
    `hash` TEXT UNIQUE,
    `name` INTEGER,
    `returnval` INTEGER,
    `calling_filename` INTEGER,
    `definition_filename` INTEGER,
    `linenum` INTEGER,
    `memory` INTEGER,
    `time` INTEGER,

    FOREIGN KEY(`name`) REFERENCES `function_names`(`ROWID`),
    FOREIGN KEY(`calling_filename`) REFERENCES `file_names`(`ROWID`),
    FOREIGN KEY(`definition_filename`) REFERENCES `file_names`(`ROWID`),
    FOREIGN KEY(`returnval`) REFERENCES `values`(`ROWID`),
    FOREIGN KEY(`memory`) REFERENCES `values`(`ROWID`),
    FOREIGN KEY(`time`) REFERENCES `values`(`ROWID`)
);

-- each function invocation has an associated set
-- of `n` parameters
CREATE TABLE `invocation_parameters`
(
    `function_invocation_hash` TEXT,
    `value_id` INTEGER,

    FOREIGN KEY(`function_invocation_hash`) REFERENCES `function_invocations`(`hash`),
    FOREIGN KEY(`value_id`) REFERENCES `values`(`ROWID`)
);

CREATE TABLE `traces`
(`requestname` TEXT, `timestamp` TEXT);

CREATE TABLE `file_names`
(`name` TEXT);
CREATE UNIQUE INDEX `idx_file_names`
ON `file_names`(`name`);

CREATE TABLE `values`
(`value` TEXT);
CREATE UNIQUE INDEX `idx_values`
ON `values`(`value`);

CREATE TABLE `function_names`
(`name` TEXT);
CREATE UNIQUE INDEX `idx_function_names`
ON `function_names`(`name`);
