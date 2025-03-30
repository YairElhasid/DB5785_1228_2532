-- dropTables.sql

-- Drop triggers and functions
DROP TRIGGER IF EXISTS enforce_max_apartments ON Apartment;
DROP FUNCTION IF EXISTS check_max_apartments;
DROP TRIGGER IF EXISTS enforce_max_rooms ON Room;
DROP FUNCTION IF EXISTS check_max_rooms;
DROP TRIGGER IF EXISTS enforce_max_people ON Rental;
DROP FUNCTION IF EXISTS check_max_people;

-- Drop tables in reverse order of dependencies
DROP TABLE IF EXISTS Maintenance_Request;
DROP TABLE IF EXISTS Rental;
DROP TABLE IF EXISTS Lease;
DROP TABLE IF EXISTS Room;
DROP TABLE IF EXISTS Apartment;
DROP TABLE IF EXISTS Building;
DROP TABLE IF EXISTS Dorm_Management;
DROP TABLE IF EXISTS student;

-- Drop ENUM types
DROP TYPE IF EXISTS gender_type;
DROP TYPE IF EXISTS priority_type;
DROP TYPE IF EXISTS major_type;