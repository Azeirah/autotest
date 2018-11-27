PRAGMA foreign_keys = ON;

CREATE TABLE `function_invocations`
(
    `name` INTEGER,
    `returnval` INTEGER,
    `calling_filename` INTEGER,
    `definition_filename` INTEGER,
    `linenum` INTEGER,

    FOREIGN KEY(`name`) REFERENCES `function_names`(`ROWID`),
    FOREIGN KEY(`calling_filename`) REFERENCES `file_names`(`ROWID`),
    FOREIGN KEY(`definition_filename`) REFERENCES `file_names`(`ROWID`),
    FOREIGN KEY(`returnval`) REFERENCES `values`(`ROWID`)
);

-- each function invocation has an associated set
-- of `n` parameters
CREATE TABLE `invocation_parameters`
(
    `function_invocation_id` INTEGER,
    `value_id` INTEGER,

    FOREIGN KEY(`function_invocation_id`) REFERENCES `function_invocations`(`ROWID`),
    FOREIGN KEY(`value_id`) REFERENCES `values`(`ROWID`)
);

CREATE TABLE `traces`
(`requestname` TEXT, `timestamp` TEXT);

CREATE TABLE `file_names`
(`name` TEXT);
CREATE INDEX `idx_file_names`
ON `file_names` (`name`);

CREATE TABLE `values`
(`value` TEXT);
CREATE INDEX `idx_values`
ON `values` (`value`);

CREATE TABLE `function_names`
(`name` TEXT);
