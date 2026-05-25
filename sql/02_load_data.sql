-- Load Users
\COPY users FROM '/Users/emily/Downloads/ai-chat-retention-analysis/data/user_cohorts.csv' WITH (FORMAT csv, HEADER true);

-- Load Events
\COPY events FROM '/Users/emily/Downloads/ai-chat-retention-analysis/data/user_events_raw.csv' WITH (FORMAT csv, HEADER true);