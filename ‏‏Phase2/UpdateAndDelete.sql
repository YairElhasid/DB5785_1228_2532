-- Update Query 1: Increases the discount by 3% for students 
-- who are renting an apartment and have no maintenance requests, 
-- ensuring the discount does not exceed 15%.
UPDATE lease l
SET discountpercent = LEAST(discountpercent + 3, 15)
WHERE EXISTS (
    SELECT 1
    FROM rental r
    JOIN student s ON r.studentid = s.studentid
    JOIN room rm ON r.roomid = rm.roomid
    LEFT JOIN maintenance_request mr ON rm.roomid = mr.roomid
    WHERE r.leaseid = l.leaseid
    GROUP BY s.studentid
    HAVING COUNT(mr.requestid) = 0
);

-- Update Query 2: Increases the maximum number of occupants by 1 in 
-- rooms of completely vacant apartments, following renovation.
UPDATE room r
SET maxpeople = maxpeople + 1
WHERE EXISTS (
    SELECT *
    FROM apartment a
    WHERE r.apartmentid = a.apartmentid
    AND r.buildingid = a.buildingid
    AND NOT EXISTS (
        SELECT *
        FROM rental rt
        JOIN room r2 ON rt.roomid = r2.roomid
        WHERE r2.apartmentid = a.apartmentid
        AND r2.buildingid = a.buildingid
        AND CURRENT_DATE BETWEEN rt.checkindate AND rt.checkoutdate
    )
);

-- Update Query 3: Adds balconies to rooms on the top floors of buildings in Jerusalem, 
-- following a city-wide renovation permit.
UPDATE room r
SET hasbalcony = TRUE
WHERE hasbalcony = FALSE
AND EXISTS (
    SELECT *
    FROM apartment a
    JOIN building b ON a.buildingid = b.buildingid
    WHERE r.apartmentid = a.apartmentid
    AND r.buildingid = a.buildingid
    AND b.address LIKE '%Jerusalem%'
    AND a.floornumber = (
        SELECT MAX(floornumber)
        FROM apartment a2
        WHERE a2.buildingid = b.buildingid
    )
);

-- Deletion Query 1: Deletes the student who submitted more than 5 maintenance requests 
-- in the past year and has the highest number of requests.
DELETE FROM student
WHERE studentid = (
    SELECT s.studentid
    FROM student s
    JOIN rental r ON s.studentid = r.studentid
    JOIN room rm ON r.roomid = rm.roomid
    JOIN maintenance_request mr ON rm.roomid = mr.roomid
    WHERE mr.requestdate >= CURRENT_DATE - INTERVAL '1 year'
    GROUP BY s.studentid
    HAVING COUNT(mr.requestid) > 5
    ORDER BY COUNT(mr.requestid) DESC
    LIMIT 1
);

-- Deletion Query 2: Deletes inactive managers who neither handled maintenance requests
-- nor issued leases, as part of staff optimization.
-- Step 1: Update the Building table to reassign buildings to an interim manager (ManagerID = 101)
UPDATE building
SET managerid = 101
WHERE managerid IN (
    SELECT dm.managerID
    FROM dorm_management dm
    WHERE NOT EXISTS (
        SELECT 1
        FROM maintenance_request mr
        WHERE mr.managerid = dm.managerid
    )
    AND NOT EXISTS (
        SELECT 1
        FROM Lease l
        WHERE l.ManagerID = dm.ManagerID
    )
);

-- Step 2: Delete the inactive managers
DELETE FROM Dorm_Management
WHERE ManagerID IN (
    SELECT dm.ManagerID
    FROM Dorm_Management dm
    WHERE NOT EXISTS (
        SELECT 1
        FROM Maintenance_Request mr
        WHERE mr.ManagerID = dm.ManagerID
    )
    AND NOT EXISTS (
        SELECT 1
        FROM Lease l
        WHERE l.ManagerID = dm.ManagerID
    )
);



-- Deletion Query 3: Deletes apartments with no rooms and buildings with no apartments.
-- This query performs two operations: 
-- 1. Deletes all apartments (from the Apartment table) that have no associated rooms in the Room table.
-- 2. Deletes all buildings (from the Building table) that have no associated apartments in the Apartment table.
-- This ensures that the database does not contain empty apartments (without rooms) or empty buildings (without apartments).
-- Part 1: Delete apartments with no rooms
DELETE FROM Apartment a
WHERE NOT EXISTS (
    SELECT 1
    FROM Room r
    WHERE r.ApartmentID = a.ApartmentID
    AND r.BuildingID = a.BuildingID
);

-- Part 2: Delete buildings with no apartments
DELETE FROM Building b
WHERE NOT EXISTS (
    SELECT 1
    FROM Apartment a
    WHERE a.BuildingID = b.BuildingID
);