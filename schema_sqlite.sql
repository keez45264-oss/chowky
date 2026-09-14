-- Chowky — SQLite schema (local development only)
-- Postgres production schema lives in schema.sql — keep both in sync manually
-- when you add/change tables.

CREATE TABLE cities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    state TEXT,
    is_single_zone INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_id INTEGER NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city_id, name)
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    pseudonym TEXT NOT NULL UNIQUE,
    home_zone_id INTEGER REFERENCES zones(id) ON DELETE SET NULL,
    current_zone_id INTEGER REFERENCES zones(id) ON DELETE SET NULL,
    is_banned INTEGER DEFAULT 0,
    is_admin INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tribes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_id INTEGER NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city_id, name)
);

CREATE TABLE tribe_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tribe_id INTEGER NOT NULL REFERENCES tribes(id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, tribe_id)
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    zone_id INTEGER REFERENCES zones(id) ON DELETE CASCADE,
    tribe_id INTEGER REFERENCES tribes(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    image_url TEXT,
    tag TEXT,
    is_anonymous INTEGER DEFAULT 0,
    is_breaking INTEGER DEFAULT 0,
    breaking_confirms INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    report_count INTEGER DEFAULT 0,
    is_hidden INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (zone_id IS NOT NULL OR tribe_id IS NOT NULL)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE likes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, user_id)
);

CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    reporter_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, reporter_id)
);

-- Seed data — launch cities
INSERT INTO cities (name, state, is_single_zone) VALUES
    ('Mumbai', 'Maharashtra', 0),
    ('Pune', 'Maharashtra', 0),
    ('Thane', 'Maharashtra', 0),
    ('Navi Mumbai', 'Maharashtra', 0),
    ('Panvel', 'Maharashtra', 0),
    ('Latur', 'Maharashtra', 1),
    ('Delhi', NULL, 0),
    ('Bangalore', NULL, 0),
    ('Hyderabad', NULL, 0),
    ('Chennai', NULL, 0),
    ('Kota', NULL, 1);

-- Navi Mumbai zones
INSERT INTO zones (city_id, name)
SELECT id, 'Digha-Airoli' FROM cities WHERE name = 'Navi Mumbai';
INSERT INTO zones (city_id, name)
SELECT id, 'Rabale-Ghansoli' FROM cities WHERE name = 'Navi Mumbai';
INSERT INTO zones (city_id, name)
SELECT id, 'Kopar Khairane-Turbhe' FROM cities WHERE name = 'Navi Mumbai';
INSERT INTO zones (city_id, name)
SELECT id, 'Vashi-Sanpada' FROM cities WHERE name = 'Navi Mumbai';
INSERT INTO zones (city_id, name)
SELECT id, 'Juinagar-Nerul' FROM cities WHERE name = 'Navi Mumbai';

-- Panvel zones
INSERT INTO zones (city_id, name)
SELECT id, 'Seawoods-CBD Belapur' FROM cities WHERE name = 'Panvel';
INSERT INTO zones (city_id, name)
SELECT id, 'Kharghar' FROM cities WHERE name = 'Panvel';
INSERT INTO zones (city_id, name)
SELECT id, 'Kalamboli-Kamothe' FROM cities WHERE name = 'Panvel';
INSERT INTO zones (city_id, name)
SELECT id, 'Panvel City' FROM cities WHERE name = 'Panvel';

-- Pune zones
INSERT INTO zones (city_id, name)
SELECT id, 'Kothrud-Karve Nagar' FROM cities WHERE name = 'Pune';
INSERT INTO zones (city_id, name)
SELECT id, 'Baner-Aundh' FROM cities WHERE name = 'Pune';
INSERT INTO zones (city_id, name)
SELECT id, 'Viman Nagar-Kalyani Nagar' FROM cities WHERE name = 'Pune';
INSERT INTO zones (city_id, name)
SELECT id, 'Hadapsar-Kondhwa' FROM cities WHERE name = 'Pune';
INSERT INTO zones (city_id, name)
SELECT id, 'Camp-Deccan' FROM cities WHERE name = 'Pune';

-- Starter tribes for Pune (example — repeat this pattern per city as you launch it)
INSERT INTO tribes (city_id, name, description)
SELECT id, 'Reading', 'Book lovers and reading circles' FROM cities WHERE name = 'Pune';
INSERT INTO tribes (city_id, name, description)
SELECT id, 'Running', 'Runners and running groups' FROM cities WHERE name = 'Pune';
INSERT INTO tribes (city_id, name, description)
SELECT id, 'Trekking', 'Weekend treks and hikes' FROM cities WHERE name = 'Pune';
INSERT INTO tribes (city_id, name, description)
SELECT id, 'Photography', 'Photo walks and gear talk' FROM cities WHERE name = 'Pune';
INSERT INTO tribes (city_id, name, description)
SELECT id, 'Study Group', 'Exam prep and study meetups' FROM cities WHERE name = 'Pune';
