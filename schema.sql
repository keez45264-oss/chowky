-- Chowky — Database Schema
-- Compatible with SQLite (local dev) and PostgreSQL (production on Render)
-- Notes:
--   - Use INTEGER PRIMARY KEY AUTOINCREMENT for SQLite, SERIAL PRIMARY KEY for Postgres
--   - This file is written in Postgres syntax; swap SERIAL -> INTEGER PRIMARY KEY AUTOINCREMENT for SQLite

-- ========================================
-- CITIES
-- ========================================
CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,       -- e.g. 'Pune', 'Mumbai', 'Latur'
    state VARCHAR(100),                       -- e.g. 'Maharashtra'
    is_single_zone BOOLEAN DEFAULT FALSE,     -- TRUE for smaller cities like Latur
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- ZONES (sub-areas within a city)
-- ========================================
CREATE TABLE zones (
    id SERIAL PRIMARY KEY,
    city_id INTEGER NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,               -- e.g. 'Kothrud-Karve Nagar'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city_id, name)
);

-- ========================================
-- USERS
-- ========================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,      -- werkzeug generate_password_hash
    pseudonym VARCHAR(50) NOT NULL UNIQUE,    -- display name shown on posts
    home_zone_id INTEGER REFERENCES zones(id) ON DELETE SET NULL,
    current_zone_id INTEGER REFERENCES zones(id) ON DELETE SET NULL, -- if traveling
    is_banned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- TRIBES (interest communities, scoped per city)
-- ========================================
CREATE TABLE tribes (
    id SERIAL PRIMARY KEY,
    city_id INTEGER NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,               -- e.g. 'Running', 'Poetry', 'Trekking'
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city_id, name)
);

-- ========================================
-- TRIBE MEMBERSHIPS (many-to-many: users <-> tribes)
-- ========================================
CREATE TABLE tribe_members (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tribe_id INTEGER NOT NULL REFERENCES tribes(id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, tribe_id)
);

-- ========================================
-- POSTS
-- ========================================
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    zone_id INTEGER REFERENCES zones(id) ON DELETE CASCADE,   -- NULL if posted only to a tribe
    tribe_id INTEGER REFERENCES tribes(id) ON DELETE CASCADE, -- NULL if posted only to a zone
    content TEXT NOT NULL,
    image_url VARCHAR(255),
    tag VARCHAR(20),                          -- 'news', 'confession', 'question', 'event', 'chitchat'
    is_anonymous BOOLEAN DEFAULT FALSE,
    is_breaking BOOLEAN DEFAULT FALSE,         -- v2: breaking-local tag
    breaking_confirms INTEGER DEFAULT 0,       -- v2: community confirmations
    like_count INTEGER DEFAULT 0,
    report_count INTEGER DEFAULT 0,
    is_hidden BOOLEAN DEFAULT FALSE,           -- auto-hidden after report threshold
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (zone_id IS NOT NULL OR tribe_id IS NOT NULL)  -- must belong to at least one
);

-- ========================================
-- COMMENTS
-- ========================================
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- LIKES
-- ========================================
CREATE TABLE likes (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, user_id)   -- prevents double-liking
);

-- ========================================
-- REPORTS
-- ========================================
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    reporter_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, reporter_id)  -- one report per user per post
);

-- ========================================
-- SEED DATA — Launch cities
-- ========================================
INSERT INTO cities (name, state, is_single_zone) VALUES
    ('Mumbai', 'Maharashtra', FALSE),
    ('Pune', 'Maharashtra', FALSE),
    ('Thane', 'Maharashtra', FALSE),
    ('Navi Mumbai', 'Maharashtra', FALSE),
    ('Panvel', 'Maharashtra', FALSE),
    ('Latur', 'Maharashtra', TRUE),
    ('Delhi', NULL, FALSE),
    ('Bangalore', NULL, FALSE),
    ('Hyderabad', NULL, FALSE),
    ('Chennai', NULL, FALSE),
    ('Kota', NULL, TRUE);

-- Navi Mumbai zones (Digha through Nerul, grouped)
-- Adjust city_id to match Navi Mumbai's actual id after insert
-- INSERT INTO zones (city_id, name) VALUES
--     (4, 'Digha-Airoli'),
--     (4, 'Rabale-Ghansoli'),
--     (4, 'Kopar Khairane-Turbhe'),
--     (4, 'Vashi-Sanpada'),
--     (4, 'Juinagar-Nerul');

-- Panvel zones (Seawoods onward, south of Nerul)
-- Adjust city_id to match Panvel's actual id after insert
-- INSERT INTO zones (city_id, name) VALUES
--     (5, 'Seawoods-CBD Belapur'),
--     (5, 'Kharghar'),
--     (5, 'Kalamboli-Kamothe'),
--     (5, 'Panvel City');

-- Example zone seed data for Pune (id lookup assumes Pune is inserted 2nd, adjust as needed)
-- INSERT INTO zones (city_id, name) VALUES
--     (2, 'Kothrud-Karve Nagar'),
--     (2, 'Baner-Aundh'),
--     (2, 'Viman Nagar-Kalyani Nagar'),
--     (2, 'Hadapsar-Kondhwa'),
--     (2, 'Camp-Deccan');

-- Example starter tribes for Pune
-- INSERT INTO tribes (city_id, name, description) VALUES
--     (2, 'Reading', 'Book lovers and reading circles'),
--     (2, 'Running', 'Runners and running groups'),
--     (2, 'Trekking', 'Weekend treks and hikes'),
--     (2, 'Photography', 'Photo walks and gear talk'),
--     (2, 'Study Group', 'Exam prep and study meetups');
