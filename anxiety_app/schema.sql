DROP TABLE IF EXISTS category_results;
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS answers;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS questions_categories;
DROP TABLE IF EXISTS tests;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username VARCHAR(20) NOT NULL,
    first_name VARCHAR(20) NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    date_created DATETIME NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    same_answers BOOLEAN
);

CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    test_id INTEGER NOT NULL,
    test_result INTEGER NOT NULL,
    hash VARCHAR(32) NOT NULL,
    user_id INTEGER,
    keyword TEXT NOT NULL,
    date DATETIME NOT NULL DEFAULT CURRENT_DATE,
    FOREIGN KEY(test_id) REFERENCES tests(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS category_results (
    result_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    result INTEGER NOT NULL,
    FOREIGN KEY(result_id) REFERENCES results(id),
    FOREIGN KEY(category_id) REFERENCES questions_categories(id)
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    test_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    question_number INTEGER NOT NULL,
    category_id INTEGER,
    FOREIGN KEY(test_id) REFERENCES tests(id),
    FOREIGN KEY(category_id) REFERENCES questions_categories(id)
);

CREATE TABLE IF NOT EXISTS questions_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS answers (
    test_id INTEGER,
    question_id INTEGER,
    answer TEXT NOT NULL,
    value INTEGER,
    FOREIGN KEY(question_id) REFERENCES questions(id),
    FOREIGN KEY(test_id) REFERENCES tests(id)
);