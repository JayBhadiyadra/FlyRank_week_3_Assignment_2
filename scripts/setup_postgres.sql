-- One-time local PostgreSQL setup for Assignment 2 (no Docker).
-- Run as a superuser (often the `postgres` user), for example:
--   psql -U postgres -f scripts/setup_postgres.sql

-- Create the application database if it does not exist.
-- Note: CREATE DATABASE cannot run inside a transaction block in some clients;
-- if needed, run the CREATE DATABASE line by itself first.
SELECT 'CREATE DATABASE tasks'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'tasks')\gexec

-- Optional: dedicated role (skip if you prefer connecting as postgres)
-- DO
-- $$
-- BEGIN
--   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'tasks') THEN
--     CREATE ROLE tasks LOGIN PASSWORD 'tasks';
--   END IF;
-- END
-- $$;
-- GRANT ALL PRIVILEGES ON DATABASE tasks TO tasks;
