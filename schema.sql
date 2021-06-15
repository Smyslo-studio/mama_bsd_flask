CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title varchar(32) not null,
    url varchar(64) not null,
    tags varchar(64) not null,
    ingredients text not null,
    recipe text not null
);

CREATE TABLE  IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title varchar(32) not null
);

CREATE TABLE  IF NOT EXISTS tags_recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe INTEGER,
    tag INTEGER
);


