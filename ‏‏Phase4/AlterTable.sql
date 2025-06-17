-- AlterTable.sql
-- Creation of tables required for logging and archiving

-- Create change_log table for log_changes trigger
CREATE TABLE IF NOT EXISTS change_log (
    log_id SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    operation VARCHAR(10) NOT NULL,
    record_id INTEGER NOT NULL,
    description TEXT,
    log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create rental_archive table for archive_old_rentals procedure
CREATE TABLE IF NOT EXISTS rental_archive (
    leaseid INTEGER,
    studentid INTEGER,
    roomid INTEGER,
    checkindate DATE,
    checkoutdate DATE,
    archive_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (leaseid)
);