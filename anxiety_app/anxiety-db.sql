-- FOR POSTGRESQL
DROP TABLE IF EXISTS api_quote;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS tests;
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS category_results;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS questions_categories;
DROP TABLE IF EXISTS answers;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(20) NOT NULL,
    first_name VARCHAR(20) NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    date_created DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE tests (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    same_answers BOOLEAN
);

CREATE TABLE results (
    id SERIAL PRIMARY KEY,
    test_id INTEGER NOT NULL,
    test_result INTEGER NOT NULL,
    hash VARCHAR(32) NOT NULL,
    user_id INTEGER,
    keyword TEXT NOT NULL,
    date DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE category_results (
    result_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    result INTEGER NOT NULL
);

CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    test_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    question_number INTEGER NOT NULL,
    category_id INTEGER
);

CREATE TABLE questions_categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE answers (
    test_id INTEGER,
    question_id INTEGER,
    answer TEXT NOT NULL,
    value INTEGER NOT NULL
);

CREATE TABLE api_quote (
    id SERIAL PRIMARY KEY,
    quote TEXT NOT NULL,
    author TEXT NOT NULL,
    fetch_date INTEGER NOT NULL
);

INSERT INTO tests (name, slug, same_answers) VALUES ('Anxiety Test', 'anxiety-test', TRUE);

INSERT INTO questions_categories (name)
VALUES
    ('Generalized Anxiety'),
    ('Social Anxiety'),
    ('Agoraphobia'),
    ('Physical Symptomps');

INSERT INTO questions (question, test_id, question_number, category_id) 
VALUES
    ('I tend to think too much about the future.', 1, 1, 1),
    ('In my everyday life, I have felt sudden fear, apparently for no reason.', 1, 2, 1),
    ('Usually, I worry excessively about everyday things.', 1, 3, 1),
    ('I sweat in an abnormal way.', 1, 4, 4),
    ('During the day I feel tired and with not enough energy.', 1, 5, 4),
    ('Even on small tasks, I have a hard time trying to concentrate.', 1, 6, 1),
    ('I have a hard time making decisions on my own, I tend to overanalyze things.', 1, 7, 1),
    ('I feel restless and have trouble relaxing.', 1, 8, 1),
    ('I always get irritated easily.', 1, 9, 1),
    ('I feel fear of leaving my house.', 1, 10, 3),
    ('Often I feel like something bad can happen or that I''m about to lose control.', 1, 11, 3),
    ('I have fear of being humiliated or ridiculed in public.', 1, 12, 2),
    ('I have had a hard time making eye contact or talking to people I don''t know.', 1, 13, 2),
    ('Whenever I go out I feel like everyone is watching and judging me.', 1, 14, 2),
    ('When in social situations, I think too much of what I''m going to say for fear to offend someone.', 1, 15, 2),
    ('I feel fear of being in enclosed spaces.', 1, 16, 3),
    ('I''m not able to remember things easily.', 1, 17, 1),
    ('I don''t attend social events or I leave early.', 1, 18, 2),
    ('I tend to evade the crowds.', 1, 19, 3),
    ('I fear traveling or doing things alone.', 1, 20, 3),
    ('I have had a hard time swallowing, like feeling a strange sensation.', 1, 21, 4),
    ('I have had digestive problems (nausea, vomiting, abdominal pain, diarrhea, constipation, borborygmi, burning sensations).', 1, 22, 4),
    ('I have experimented tachycardia (rapid heart rate).', 1, 23, 4),
    ('Sometimes I have trouble breathing, like feeling out of breath.', 1, 24, 4),
    ('It''s hard for me to fall asleep or stay asleep.', 1, 25, 1);

INSERT INTO answers (question_id, test_id, answer, value)
VALUES
    (1, 1, 'Never', 0),
    (1, 1, 'Rarely', 1),
    (1, 1, 'Sometimes', 2),
    (1, 1, 'Most of the time', 3),
    (1, 1, 'Always', 4);