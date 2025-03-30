-- insertTables.sql

-- Insert into student (3 records)
INSERT INTO student (StudentID, FirstName, LastName, Gender, DateOfBirth, EnrollmentDate, PhoneNumber, Email, Major) VALUES
(1, 'Noa', 'Levi', 'Female', '2002-04-15', '2023-09-01', '+972 52-123-4567', 'noa.levi@university.ac.il', 'Computer Science'),
(2, 'Eitan', 'Cohen', 'Male', '2001-08-22', '2023-09-01', '+972 54-987-6543', 'eitan.cohen@university.ac.il', 'Mathematics'),
(3, 'Shira', 'Ben-David', 'Female', '2000-12-10', '2022-09-01', '+972 57-555-5555', 'shira.bendavid@university.ac.il', 'Biology');

-- Insert into Dorm_Management (3 records)
INSERT INTO Dorm_Management (ManagerID, FullName, PhoneNumber, Email, HireDate) VALUES
(1, 'Yossi Mizrahi', '+972 53-111-2222', 'yossi.mizrahi@university.ac.il', '2020-01-15'),
(2, 'Tamar Avraham', '+972 50-333-4444', 'tamar.avraham@university.ac.il', '2019-06-01'),
(3, 'Avi Peretz', '+972 58-666-7777', 'avi.peretz@university.ac.il', '2021-03-10');

-- Insert into Building (3 records)
-- MaxApartments is set to allow at least 1 apartment per building (we'll insert 1 apartment per building)
INSERT INTO Building (BuildingID, BuildingName, Address, MaxApartments, ManagerID) VALUES
(1, 'Binyan Alef', 'Rehov HaUniversita 1, Jerusalem', 2, 1),
(2, 'Binyan Bet', 'Rehov HaCampus 2, Tel Aviv', 2, 2),
(3, 'Binyan Gimel', 'Rehov HaDorm 3, Haifa', 2, 3);

-- Insert into Apartment (3 records)
-- Each building gets 1 apartment (MaxApartments = 2, so this is fine)
-- MaxRooms is set to allow at least 1 room per apartment (we'll insert 1 room per apartment)
INSERT INTO Apartment (ApartmentID, BuildingID, RoomCapacity, FloorNumber, MaxRooms) VALUES
(1, 1, 4, 1, 2), -- Apartment 1 in Building 1
(1, 2, 3, 2, 2), -- Apartment 1 in Building 2
(1, 3, 5, 3, 2); -- Apartment 1 in Building 3

-- Insert into Room (3 records)
-- Each apartment gets 1 room (MaxRooms = 2, so this is fine)
-- MaxPeople is set to allow at least 1 student per room (we'll insert 1 student per room)
INSERT INTO Room (RoomID, MaxPeople, HasBalcony, ApartmentID, BuildingID) VALUES
(1, 2, TRUE, 1, 1),  -- Room 1 in Apartment 1, Building 1
(2, 2, FALSE, 1, 2),  -- Room 2 in Apartment 1, Building 2
(3, 2, TRUE, 1, 3);   -- Room 3 in Apartment 1, Building 3

-- Insert into Lease (3 records)
INSERT INTO Lease (LeaseID, ContractDate, DiscountPercent, ManagerID) VALUES
(1, '2024-08-01', 10.00, 1), -- Managed by Yossi
(2, '2024-08-15', 5.50, 2),  -- Managed by Tamar
(3, '2024-09-01', 0.00, 3);  -- Managed by Avi

-- Insert into Rental (3 records)
-- Each room gets 1 student (MaxPeople = 2, so this is fine)
-- Dates include March 27, 2025 (CURRENT_DATE) to be considered active
INSERT INTO Rental (StudentID, RoomID, LeaseID, CheckInDate, CheckOutDate) VALUES
(1, 1, 1, '2025-01-01', '2025-12-31'), -- Noa in Room 1 (Building 1)
(2, 2, 2, '2025-01-01', '2025-12-31'), -- Eitan in Room 2 (Building 2)
(3, 3, 3, '2025-01-01', '2025-12-31'); -- Shira in Room 3 (Building 3)

-- Insert into Maintenance_Request (3 records)
-- We'll include a mix: one tied to a rental, one with only StudentID, and one with no student/room/lease
INSERT INTO Maintenance_Request (RequestID, IssueDescription, RequestDate, ResolvedDate, Priority, ManagerID, StudentID, RoomID, LeaseID) VALUES
(1, 'Leaky faucet in room', '2025-03-01', '2025-03-05', 'High', 1, 1, 1, 1), -- Noa's request for Room 1
(2, 'Broken window in hallway', '2025-03-02', NULL, 'Medium', 2, 2, NULL, NULL), -- Eitan's request, not tied to a room
(3, 'Elevator not working', '2025-03-03', '2025-03-04', 'High', 3, NULL, NULL, NULL); -- General request, no student