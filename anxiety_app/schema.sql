DROP TABLE IF EXISTS answers;
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS tests;

CREATE TABLE IF NOT EXISTS tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    total_questions INTEGER NOT NULL,
    same_answers BOOLEAN
);

CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    test_id INTEGER NOT NULL,
    test_result INTEGER NOT NULL,
    hash VARCHAR(24) NOT NULL,
    user_id INTEGER,
    FOREIGN KEY(test_id) REFERENCES tests(id)
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    test_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    question_number INTEGER NOT NULL,
    FOREIGN KEY(test_id) REFERENCES tests(id)
);

CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    test_id INTEGER,
    question_id INTEGER,
    answer TEXT NOT NULL,
    value INTEGER,
    FOREIGN KEY(question_id) REFERENCES questions(id),
    FOREIGN KEY(test_id) REFERENCES tests(id)
);

INSERT INTO tests (name, slug, total_questions, same_answers) VALUES("Anxiety Test", "anxiety-test", 3, 1);

INSERT INTO questions (question, test_id, question_number) 
VALUES
    ("Fidgeting, restlessness or pacing, tremor of hands, furrowed brow, strained face, sighing or rapid respiration, facial pallor, swallowing, etc.", 1, 1),
    ("What do you think about this website in general?", 1, 2),
    ("Do you believe that you can become someone that no one thinks you can be?, or its all a lie?", 1, 3);

INSERT INTO answers (question_id, test_id, answer, value)
VALUES
    (1, 1, "Not possible", 3),
    (1, 1, "I don't know", 5),
    (1, 1, "More less", 5);