-- Constraint 1: CHECK on DiscountPercent in Lease table
ALTER TABLE Lease
ADD CONSTRAINT check_discountpercent_range
CHECK (DiscountPercent >= 0 AND DiscountPercent <= 100);

-- Test violation: Try updating a lease with invalid DiscountPercent (should fail)
UPDATE Lease
SET DiscountPercent = 300
WHERE LeaseID = 1;

-- Constraint 2: NOT NULL andCHECK on PhoneNumber in student table
ALTER TABLE student
ALTER COLUMN PhoneNumber SET NOT NULL;

ALTER TABLE student
ADD CONSTRAINT check_student_phonenumber
CHECK (PhoneNumber ~ '^\+972 5[0-9]-[0-9]{3}-[0-9]{4}$');

-- Test violation: Try inserting a student with invalid PhoneNumber (should fail)
INSERT INTO student (StudentID, FirstName, LastName, Gender, DateOfBirth, EnrollmentDate, PhoneNumber, Email, Major)
VALUES (999, 'Test', 'Student', 'Male', '2000-01-01', '2023-09-01', '123-456-7890', 'test@example.com', 'Computer Science');

-- Test violation: Try inserting a student with NULL PhoneNumber (should fail)
INSERT INTO student (StudentID, FirstName, LastName, Gender, DateOfBirth, EnrollmentDate, PhoneNumber, Email, Major)
VALUES (998, 'Test', 'Student', 'Male', '2000-01-01', '2023-09-01', NULL, 'test@example.com', 'Computer Science');

-- Constraint 3: NOT NULL and CHECK on CheckOutDate in Rental table
ALTER TABLE Rental
ALTER COLUMN CheckOutDate SET NOT NULL;

ALTER TABLE Rental
ADD CONSTRAINT check_checkout_after_checkin
CHECK (CheckOutDate > CheckInDate);

-- Test violation: Try inserting a rental with CheckOutDate before CheckInDate (should fail)
INSERT INTO Rental (StudentID, RoomID, LeaseID, CheckInDate, CheckOutDate)
VALUES (301, 100, 401, '2025-04-01', '2025-03-01');

-- Test violation: Try inserting a rental with NULL CheckOutDate (should fail)
INSERT INTO Rental (StudentID, RoomID, LeaseID, CheckInDate, CheckOutDate)
VALUES (301, 100, 401, '2025-04-01', NULL);


--We decided to update the database following the deletion of one of these factors.
-- Drop the existing foreign key constraints
ALTER TABLE Rental
DROP CONSTRAINT rental_studentid_fkey;

ALTER TABLE Rental
DROP CONSTRAINT rental_roomid_fkey;

ALTER TABLE Rental
DROP CONSTRAINT rental_leaseid_fkey;

-- Add the foreign key constraints with ON DELETE CASCADE
ALTER TABLE Rental
ADD CONSTRAINT rental_studentid_fkey
FOREIGN KEY (StudentID) REFERENCES student(StudentID) ON DELETE CASCADE;

ALTER TABLE Rental
ADD CONSTRAINT rental_roomid_fkey
FOREIGN KEY (RoomID) REFERENCES Room(RoomID) ON DELETE CASCADE;

ALTER TABLE Rental
ADD CONSTRAINT rental_leaseid_fkey
FOREIGN KEY (LeaseID) REFERENCES Lease(LeaseID) ON DELETE CASCADE;

-- Drop the existing foreign key constraint in Maintenance_Request
ALTER TABLE Maintenance_Request
DROP CONSTRAINT maintenance_request_studentid_roomid_leaseid_fkey;

-- Add the foreign key constraint with ON DELETE CASCADE
ALTER TABLE Maintenance_Request
ADD CONSTRAINT maintenance_request_studentid_roomid_leaseid_fkey
FOREIGN KEY (StudentID, RoomID, LeaseID) REFERENCES Rental(StudentID, RoomID, LeaseID) ON DELETE CASCADE;