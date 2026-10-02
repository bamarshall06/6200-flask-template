-- The tables this project needs.
--
-- Run this against your database once. Your database already exists - it was
-- created with your app and carries the same name. In Database + SQL you
-- replace the `examples` table below with
-- tables of your own.

CREATE TABLE IF NOT EXISTS examples (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
