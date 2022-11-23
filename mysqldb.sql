--

-- File generated with SQLiteStudio v3.2.1 on Wed Nov 23 00:10:57 2022

--

-- Text encoding used: UTF-8

--

PRAGMA foreign_keys = off;



-- Table: fixture

CREATE TABLE fixture (id INTEGER NOT NULL, team1 VARCHAR (100) NOT NULL, team2 VARCHAR (100) NOT NULL, is_finished BOOLEAN NOT NULL, score1 INTEGER, score2 INTEGER, PRIMARY KEY (id));

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (1, 'Qatar', 'Ecuador', 1, 0, 2);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (2, 'England', 'Iran', 1, 6, 2);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (3, 'Senegal', 'Netherlands', 1, 0, 2);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (4, 'USA', 'Wales', 1, 1, 1);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (5, 'Argentina', 'Saudi Arabia', 1, 1, 2);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (6, 'Denmark', 'Tunisia', 1, 0, 0);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (7, 'Mexico', 'Poland', 1, 0, 0);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (8, 'France', 'Australia', 1, 4, 1);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (9, 'Morocco', 'Croatia', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (10, 'Germany', 'Japan', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (11, 'Spain', 'Costa Rica', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (12, 'Belgium', 'Canada', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (13, 'Switzerland', 'Cameroon', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (14, 'Uruguay', 'Korea Republic', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (15, 'Portugal', 'Ghana', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (16, 'Brazil', 'Serbia', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (17, 'Wales', 'Iran', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (18, 'Qatar', 'Senegal', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (19, 'Netherlands', 'Ecuador', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (20, 'England', 'USA', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (21, 'Tunisia', 'Australia', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (22, 'Poland', 'Saudi Arabia', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (23, 'France', 'Denmark', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (24, 'Argentina', 'Mexico', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (25, 'Japan', 'Costa Rica', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (26, 'Belgium', 'Morocco', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (27, 'Croatia', 'Canada', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (28, 'Spain', 'Germany', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (29, 'Cameroon', 'Serbia', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (30, 'Korea Republic', 'Ghana', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (31, 'Brazil', 'Switzerland', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (32, 'Portugal', 'Uruguay', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (33, 'Ecuador', 'Senegal', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (34, 'Netherlands', 'Qatar', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (35, 'Wales', 'England', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (36, 'Iran', 'USA', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (37, 'Australia', 'Denmark', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (38, 'Tunisia', 'France', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (39, 'Poland', 'Argentina', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (40, 'Saudi Arabia', 'Mexico', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (41, 'Croatia', 'Belgium', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (42, 'Canada', 'Morocco', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (43, 'Japan', 'Spain', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (44, 'Costa Rica', 'Germany', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (45, 'Ghana', 'Uruguay', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (46, 'Korea Republic', 'Portugal', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (47, 'Serbia', 'Switzerland', 0, NULL, NULL);

INSERT INTO fixture (id, team1, team2, is_finished, score1, score2) VALUES (48, 'Cameroon', 'Brazil', 0, NULL, NULL);

-- Table: user

CREATE TABLE user (

        id INTEGER NOT NULL,

        username VARCHAR(100) NOT NULL,

        password VARCHAR(100) NOT NULL,

        score INTEGER NOT NULL,

        PRIMARY KEY (id),

        UNIQUE (username)

);

INSERT INTO user (id, username, password, score) VALUES (1, 'Fergal', 'sha256$VMdwmgZ2qvgDUU7C$6b9fbeb5f2ef9efae7d70e80c21972e5f5f69896b5a0c9f352a4489b02c7e130', 4);

INSERT INTO user (id, username, password, score) VALUES (2, 'Gerry', 'sha256$MS2JupYmNAFesc8M$c71640f6132f87afd487c846b9187f6081df128560e77f052bb0f7c17a6ff076', 5);

INSERT INTO user (id, username, password, score) VALUES (3, 'Rosa', 'sha256$nRwMAdoJUiQe6uqC$e56902cf34801dd1995fdf12a8b958ddf8e600ab304ca170b0699761ddbf801e', 2);

INSERT INTO user (id, username, password, score) VALUES (4, 'Jp', 'sha256$IttkB0EJMkpTyLwu$9cc1c2cb87a208b5fa44462ffb4644b812fe4d94944f286ee2472278fed0c9b3', 1);

INSERT INTO user (id, username, password, score) VALUES (5, 'KDoggyDog', 'sha256$n1B46QG3yYvvtgxI$2dbc2f1876a1ff04769adb98edc9003c31d6658641bfb351321882976a19acb6', 2);



-- Table: prediction

CREATE TABLE prediction (id INTEGER NOT NULL, user_id INTEGER NOT NULL, fixture_id INTEGER NOT NULL, score1 INTEGER NOT NULL, score2 INTEGER NOT NULL, PRIMARY KEY (id), FOREIGN KEY (user_id) REFERENCES user (id), FOREIGN KEY (fixture_id) REFERENCES fixture (id));

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (1, 1, 2, 3, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (2, 1, 4, 2, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (3, 1, 5, 3, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (4, 1, 6, 0, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (5, 1, 7, 1, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (6, 2, 4, 1, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (7, 2, 5, 2, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (8, 2, 6, 2, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (9, 2, 7, 1, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (10, 2, 8, 4, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (11, 3, 7, 1, 2);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (12, 3, 8, 3, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (13, 3, 10, 2, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (14, 3, 9, 0, 2);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (15, 3, 11, 1, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (16, 3, 20, 3, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (17, 3, 16, 2, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (18, 1, 8, 3, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (19, 1, 9, 1, 3);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (20, 1, 10, 2, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (21, 1, 11, 2, 2);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (22, 1, 12, 3, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (23, 4, 7, 1, 2);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (24, 4, 8, 2, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (25, 4, 9, 1, 3);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (26, 4, 10, 2, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (27, 4, 11, 3, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (28, 4, 12, 3, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (29, 4, 13, 0, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (30, 4, 14, 3, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (31, 4, 15, 4, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (32, 4, 16, 4, 2);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (33, 4, 17, 1, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (34, 4, 19, 3, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (35, 4, 18, 0, 4);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (36, 4, 20, 3, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (37, 4, 21, 1, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (38, 4, 22, 3, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (39, 4, 23, 2, 2);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (40, 4, 24, 3, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (41, 4, 25, 0, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (42, 5, 8, 3, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (43, 4, 26, 2, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (44, 5, 9, 1, 3);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (45, 5, 10, 2, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (46, 4, 27, 2, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (47, 5, 11, 1, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (48, 4, 28, 0, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (49, 4, 29, 1, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (50, 5, 12, 4, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (51, 4, 30, 2, 3);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (52, 5, 13, 2, 2);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (53, 4, 31, 3, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (54, 5, 14, 4, 2);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (55, 4, 32, 2, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (56, 5, 15, 2, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (57, 5, 16, 3, 2);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (58, 5, 17, 1, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (59, 4, 33, 1, 2);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (60, 4, 34, 3, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (61, 5, 18, 0, 2);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (62, 4, 35, 1, 2);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (63, 4, 36, 1, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (64, 5, 20, 3, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (65, 4, 37, 1, 2);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (66, 5, 19, 3, 2);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (67, 4, 38, 0, 4);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (68, 4, 39, 1, 3);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (69, 4, 40, 1, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (70, 4, 41, 2, 3);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (71, 4, 42, 0, 1);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (72, 4, 43, 0, 4);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (73, 4, 44, 0, 4);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (74, 4, 45, 3, 3);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (75, 4, 46, 0, 3);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (76, 4, 47, 3, 2);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (77, 4, 48, 1, 3);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (78, 3, 12, 0, 0);

INSERT INTO prediction (id, user_id, fixture_id, score1, score2) VALUES (79, 3, 13, 1, 0);



PRAGMA foreign_keys = on;

