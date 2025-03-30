-- createTables.sql

-- Create ENUM types
CREATE TYPE gender_type AS ENUM ('Male', 'Female');
CREATE TYPE priority_type AS ENUM ('Low', 'Medium', 'High');
CREATE TYPE major_type AS ENUM ('Computer Science', 'Mathematics', 'Physics', 'Biology', 'Chemistry');


-- Create the student table
CREATE TABLE student (
    StudentID INT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Gender gender_type NOT NULL,
    DateOfBirth DATE NOT NULL,
    EnrollmentDate DATE NOT NULL,
	PhoneNumber VARCHAR(16) NOT NULL CHECK (PhoneNumber ~ '^\+972 5[0-9]-[0-9]{3}-[0-9]{4}$'),
    Email VARCHAR(50) NOT NULL CHECK (Email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    Major major_type NOT NULL
);

-- Create the Dorm_Management table
CREATE TABLE Dorm_Management (
    ManagerID INT PRIMARY KEY,
    FullName VARCHAR(100) NOT NULL,
	PhoneNumber VARCHAR(16) NOT NULL CHECK (PhoneNumber ~ '^\+972 5[0-9]-[0-9]{3}-[0-9]{4}$'),
    Email VARCHAR(50) NOT NULL CHECK (Email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    HireDate DATE NOT NULL
);

-- Create the Building table
CREATE TABLE Building (
    BuildingID INT PRIMARY KEY,
    BuildingName VARCHAR(100) NOT NULL,
    Address VARCHAR(100) NOT NULL,
    MaxApartments INT NOT NULL CHECK (MaxApartments > 0),
    ManagerID INT NOT NULL,
    FOREIGN KEY (ManagerID) REFERENCES Dorm_Management(ManagerID)
);

-- Create the Apartment table
CREATE TABLE Apartment (
    ApartmentID INT NOT NULL,
    BuildingID INT NOT NULL,
    RoomCapacity INT NOT NULL CHECK (RoomCapacity > 0),
    FloorNumber INT NOT NULL,
    MaxRooms INT NOT NULL CHECK (MaxRooms > 0),
    PRIMARY KEY (ApartmentID, BuildingID),
    FOREIGN KEY (BuildingID) REFERENCES Building(BuildingID)
);

-- Create the Room table
CREATE TABLE Room (
    RoomID INT PRIMARY KEY,
    MaxPeople INT NOT NULL CHECK (MaxPeople > 0),
    HasBalcony BOOLEAN NOT NULL,
    ApartmentID INT NOT NULL,
    BuildingID INT NOT NULL,
    FOREIGN KEY (ApartmentID, BuildingID) REFERENCES Apartment(ApartmentID, BuildingID)
);

-- Create the Lease table
CREATE TABLE Lease (
    LeaseID SERIAL PRIMARY KEY,
    ContractDate DATE NOT NULL,
    DiscountPercent DECIMAL(5, 2) NOT NULL CHECK (DiscountPercent >= 0 AND DiscountPercent <= 100),
    ManagerID INT NOT NULL,
    FOREIGN KEY (ManagerID) REFERENCES Dorm_Management(ManagerID)
);

-- Create the Rental table
CREATE TABLE Rental (
    StudentID INT NOT NULL,
    RoomID INT NOT NULL,
    LeaseID INT NOT NULL,
    CheckInDate DATE NOT NULL,
    CheckOutDate DATE NOT NULL CHECK (CheckOutDate > CheckInDate),
    PRIMARY KEY (StudentID, RoomID, LeaseID),
    FOREIGN KEY (StudentID) REFERENCES student(StudentID),
    FOREIGN KEY (RoomID) REFERENCES Room(RoomID),
    FOREIGN KEY (LeaseID) REFERENCES Lease(LeaseID)
);

-- Create the Maintenance_Request table
CREATE TABLE Maintenance_Request (
    RequestID INT PRIMARY KEY,
    IssueDescription TEXT NOT NULL,
    RequestDate DATE NOT NULL,
    ResolvedDate DATE,
    Priority priority_type NOT NULL,
    ManagerID INT NOT NULL,
    StudentID INT,
    RoomID INT,
    LeaseID INT,
    FOREIGN KEY (ManagerID) REFERENCES Dorm_Management(ManagerID),
    FOREIGN KEY (StudentID, RoomID, LeaseID) REFERENCES Rental(StudentID, RoomID, LeaseID),
    CHECK (ResolvedDate IS NULL OR ResolvedDate >= RequestDate)
);

-- Triggers to enforce MAX constraints
-- Create indexes to improve trigger performance
CREATE INDEX idx_apartment_buildingid ON Apartment(BuildingID);
CREATE INDEX idx_room_apartmentid_buildingid ON Room(ApartmentID, BuildingID);
CREATE INDEX idx_rental_roomid ON Rental(RoomID);

-- 1. Enforce MaxApartments
CREATE OR REPLACE FUNCTION check_max_apartments()
RETURNS TRIGGER AS $$
DECLARE
    apartment_count INT;
    max_apartments INT;
BEGIN
    -- Count existing apartments for the building, including the new row
    SELECT COUNT(*) + 1 INTO apartment_count
    FROM Apartment
    WHERE BuildingID = NEW.BuildingID;

    -- Get the MaxApartments value, locking the row to prevent race conditions
    SELECT MaxApartments INTO max_apartments
    FROM Building
    WHERE BuildingID = NEW.BuildingID
    FOR UPDATE;

    -- Check if the count exceeds the maximum
    IF apartment_count > max_apartments THEN
        RAISE EXCEPTION 'Cannot add more apartments to Building %: MaxApartments (%) exceeded', NEW.BuildingID, max_apartments;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_max_apartments
BEFORE INSERT ON Apartment
FOR EACH ROW
EXECUTE FUNCTION check_max_apartments();

-- 2. Enforce MaxRooms
CREATE OR REPLACE FUNCTION check_max_rooms()
RETURNS TRIGGER AS $$
DECLARE
    room_count INT;
    max_rooms INT;
BEGIN
    -- Count existing rooms for the apartment, including the new row
    SELECT COUNT(*) + 1 INTO room_count
    FROM Room
    WHERE ApartmentID = NEW.ApartmentID AND BuildingID = NEW.BuildingID;

    -- Get the MaxRooms value, locking the row to prevent race conditions
    SELECT MaxRooms INTO max_rooms
    FROM Apartment
    WHERE ApartmentID = NEW.ApartmentID AND BuildingID = NEW.BuildingID
    FOR UPDATE;

    -- Check if the count exceeds the maximum
    IF room_count > max_rooms THEN
        RAISE EXCEPTION 'Cannot add more rooms to Apartment % in Building %: MaxRooms (%) exceeded', NEW.ApartmentID, NEW.BuildingID, max_rooms;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_max_rooms
BEFORE INSERT ON Room
FOR EACH ROW
EXECUTE FUNCTION check_max_rooms();

-- 3. Enforce MaxPeople
CREATE OR REPLACE FUNCTION check_max_people()
RETURNS TRIGGER AS $$
DECLARE
    people_count INT;
    max_people INT;
BEGIN
    -- Count active rentals for the room, including the new row
    SELECT COUNT(*) + 1 INTO people_count
    FROM Rental
    WHERE RoomID = NEW.RoomID
    AND CURRENT_DATE BETWEEN CheckInDate AND CheckOutDate;

    -- Get the MaxPeople value, locking the row to prevent race conditions
    SELECT MaxPeople INTO max_people
    FROM Room
    WHERE RoomID = NEW.RoomID
    FOR UPDATE;

    -- Check if the count exceeds the maximum
    IF people_count > max_people THEN
        RAISE EXCEPTION 'Cannot add more students to Room %: MaxPeople (%) exceeded', NEW.RoomID, max_people;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_max_people
BEFORE INSERT ON Rental
FOR EACH ROW
EXECUTE FUNCTION check_max_people();