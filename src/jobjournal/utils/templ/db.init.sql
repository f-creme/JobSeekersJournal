-- Creating database

-- Table "positions"
CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pub_date TEXT, 
    position TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    source TEXT,
    hype INTEGER NOT NULL CHECK (hype >= 0 AND hype <= 5),
    status INTEGER,
    salary REAL,
    details TEXT,
    skills TEXT NOT NULL CHECK (json_valid(skills)),
    motivation TEXT,
    actions TEXT NOT NULL CHECK (json_valid(actions))
);

--Table "contacts
CREATE TABLE IF NOT EXISTS contacts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    company TEXT NOT NULL,
    mail TEXT,
    phone TEXT
);

-- Table "places"
CREATE TABLE IF NOT EXISTS places(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    place TEXT NOT NULL,
    lat REAL,
    long REAL
);

-- Join table "position_places"
CREATE TABLE IF NOT EXISTS position_places(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position INTEGER,
    place INTEGER,
    FOREIGN KEY (position) REFERENCES positions(id),
    FOREIGN KEY (place) REFERENCES places(id)
);