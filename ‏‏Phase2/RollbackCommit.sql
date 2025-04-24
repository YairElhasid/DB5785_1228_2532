-- Update with ROLLBACK
-- Show initial state of the Lease table (before update)
SELECT LeaseID, DiscountPercent 
FROM Lease 
WHERE LeaseID = 400;

-- Start a transaction
BEGIN;

-- Update: Increase DiscountPercent by 5 for LeaseID 400
UPDATE Lease 
SET DiscountPercent = DiscountPercent + 5
WHERE LeaseID = 400;

-- Show state after update (before rollback)
SELECT LeaseID, DiscountPercent 
FROM Lease 
WHERE LeaseID = 400;

-- Rollback the transaction
ROLLBACK;

-- Show state after rollback (should return to initial state)
SELECT LeaseID, DiscountPercent 
FROM Lease 
WHERE LeaseID = 400;

-- Update with COMMIT
-- Show initial state of the Room table (before update)
SELECT RoomID, MaxPeople 
FROM Room 
WHERE RoomID = 400;

-- Start a transaction
BEGIN;

-- Update: Increase MaxPeople by 1 for RoomID 400
UPDATE Room 
SET MaxPeople = MaxPeople + 1
WHERE RoomID = 400;

-- Show state after update (before commit)
SELECT RoomID, MaxPeople 
FROM Room 
WHERE RoomID = 400;

-- Commit the transaction
COMMIT;

-- Show state after commit (should remain updated)
SELECT RoomID, MaxPeople 
FROM Room 
WHERE RoomID = 400;

-- We can't rollback after a commit. (should fail)
ROLLBACK;