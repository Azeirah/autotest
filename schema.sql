PRAGMA foreign_keys = ON;

CREATE TABLE `function_invocations`
(
    `name` INTEGER,
    `parameters` INTEGER,
    `returnval` TEXT,
    `calling_filename` INTEGER,
    `definition_filename` INTEGER,
    `linenum` INTEGER,

    FOREIGN KEY(`name`) REFERENCES `function_names`(`ROWID`),
    FOREIGN KEY(`calling_filename`) REFERENCES `file_names`(`ROWID`),
    FOREIGN KEY(`definition_filename`) REFERENCES `file_names`(`ROWID`),
    FOREIGN KEY(`parameters`) REFERENCES `invocation_parameters`(`ROWID`)
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

CREATE TABLE `values`
(`value` TEXT);

CREATE TABLE `function_names`
(`name` TEXT);
