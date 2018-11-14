PRAGMA foreign_keys = ON;

CREATE TABLE function_calls
(
    `name` TEXT,
    `params` TEXT,
    `returnval` TEXT,
    `calling_filename` INTEGER,
    `definition_filename` INTEGER,
    `linenum` INTEGER,

    FOREIGN KEY(`calling_filename`) REFERENCES `file_names`(`rowid`),
    FOREIGN KEY(`definition_filename`) REFERENCES `file_names`(`rowid`)
);

CREATE TABLE traces
(`requestname` TEXT, `timestamp` TEXT);

CREATE TABLE file_names
(`name` TEXT);

CREATE TABLE function_names
(`name` TEXT);
