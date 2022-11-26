.open MajorMonkey.db

CREATE TABLE IF NOT EXISTS Users (
    username VARCHAR(10) NOT NULL,
    courses BLOB NOT NULL,
    PRIMARY KEY (username)
);

CREATE TABLE IF NOT EXISTS Courses (
    subjectcode VARCHAR(10) NOT NULL,
    coursenum VARCHAR(10) NOT NULL,
    distdeg BLOB NOT NULL,
    coursetitle VARCHAR(255) NOT NULL,
    PRIMARY KEY (subjectcode, coursenum)
);

CREATE TABLE IF NOT EXISTS Degrees (
    degreename VARCHAR(20) NOT NULL,
    requirements VARCHAR(20) NOT NULL,
    electives VARCHAR(20) NOT NULL,
    PRIMARY KEY (degreename),
    FOREIGN KEY (requirements) REFERENCES Requisites(requisitename),
    FOREIGN KEY (electives) REFERENCES Requisites(requisitename)
);

CREATE TABLE IF NOT EXISTS Requisites (
    requisitename VARCHAR(20) NOT NULL,
    requisite BLOB NOT NULL,
    PRIMARY KEY (requisitename)
);
