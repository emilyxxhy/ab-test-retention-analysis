-- Drop tables if they already exist so you can rerun this safely
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS users;

-- Create the Users table (The Roster)
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    created_date DATE,
    "group" VARCHAR(50),
    device_os VARCHAR(50),
    region VARCHAR(100)
);

-- Create the Events table (The Logbook)
CREATE TABLE events (
    user_id INTEGER,
    event_timestamp TIMESTAMP,
    event_type VARCHAR(50),
    event_date DATE
);

-- Create an index to make our future retention queries run much faster
CREATE INDEX idx_events_user_id ON events(user_id);