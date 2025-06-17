-- Trigger Function 1: Log changes
CREATE OR REPLACE FUNCTION log_changes()
RETURNS TRIGGER AS $$
DECLARE
    rec_id INTEGER;
BEGIN
    CASE TG_TABLE_NAME
        WHEN 'lease' THEN
            IF NEW.leaseid IS NULL THEN
                RAISE EXCEPTION 'Missing leaseid in lease table';
            END IF;
            rec_id := NEW.leaseid;
        WHEN 'rental' THEN
            IF NEW.leaseid IS NULL THEN
                RAISE EXCEPTION 'Missing leaseid in rental table';
            END IF;
            rec_id := NEW.leaseid;
        WHEN 'maintenance_request' THEN
            IF NEW.requestid IS NULL THEN
                RAISE EXCEPTION 'Missing requestid in maintenance_request table';
            END IF;
            rec_id := NEW.requestid;
        ELSE
            RAISE EXCEPTION 'Unsupported table: %', TG_TABLE_NAME;
    END CASE;

    INSERT INTO change_log (table_name, operation, record_id, description)
    VALUES (
        TG_TABLE_NAME,
        TG_OP,
        rec_id,
        'Change in ' || TG_TABLE_NAME || ' with ID ' || rec_id || ' at ' || CURRENT_TIMESTAMP
    );

    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in log_changes: %', SQLERRM;
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Triggers for log_changes
DROP TRIGGER IF EXISTS log_changes_lease_trigger ON lease;
CREATE TRIGGER log_changes_lease_trigger
AFTER INSERT OR UPDATE ON lease
FOR EACH ROW
EXECUTE FUNCTION log_changes();

DROP TRIGGER IF EXISTS log_changes_rental_trigger ON rental;
CREATE TRIGGER log_changes_rental_trigger
AFTER INSERT OR UPDATE ON rental
FOR EACH ROW
EXECUTE FUNCTION log_changes();

DROP TRIGGER IF EXISTS log_changes_maintenance_trigger ON maintenance_request;
CREATE TRIGGER log_changes_maintenance_trigger
AFTER INSERT OR UPDATE ON maintenance_request
FOR EACH ROW
EXECUTE FUNCTION log_changes();

-- Trigger Function 2: Enforce MaxApartments
CREATE OR REPLACE FUNCTION check_max_apartments()
RETURNS TRIGGER AS $$
DECLARE
    apartment_count INT;
    max_apartments INT;
BEGIN
    SELECT COUNT(*) + 1 INTO apartment_count
    FROM Apartment
    WHERE BuildingID = NEW.BuildingID;

    SELECT MaxApartments INTO max_apartments
    FROM Building
    WHERE BuildingID = NEW.BuildingID
    FOR UPDATE;

    IF apartment_count > max_apartments THEN
        RAISE EXCEPTION 'Cannot add more apartments to Building %: MaxApartments (%) exceeded', NEW.BuildingID, max_apartments;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS enforce_max_apartments ON Apartment;
CREATE TRIGGER enforce_max_apartments
BEFORE INSERT ON Apartment
FOR EACH ROW
EXECUTE FUNCTION check_max_apartments();

-- Trigger Function 3: Enforce MaxRooms
CREATE OR REPLACE FUNCTION check_max_rooms()
RETURNS TRIGGER AS $$
DECLARE
    room_count INT;
    max_rooms INT;
BEGIN
    SELECT COUNT(*) + 1 INTO room_count
    FROM Room
    WHERE ApartmentID = NEW.ApartmentID AND BuildingID = NEW.BuildingID;

    SELECT MaxRooms INTO max_rooms
    FROM Apartment
    WHERE ApartmentID = NEW.ApartmentID AND BuildingID = NEW.BuildingID
    FOR UPDATE;

    IF room_count > max_rooms THEN
        RAISE EXCEPTION 'Cannot add more rooms to Apartment % in Building %: MaxRooms (%) exceeded', NEW.ApartmentID, NEW.BuildingID, max_rooms;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS enforce_max_rooms ON Room;
CREATE TRIGGER enforce_max_rooms
BEFORE INSERT ON Room
FOR EACH ROW
EXECUTE FUNCTION check_max_rooms();

-- Trigger Function 4: Enforce MaxPeople
CREATE OR REPLACE FUNCTION check_max_people()
RETURNS TRIGGER AS $$
DECLARE
    people_count INT;
    max_people INT;
BEGIN
    SELECT COUNT(*) + 1 INTO people_count
    FROM Rental
    WHERE RoomID = NEW.RoomID
    AND CURRENT_DATE BETWEEN CheckInDate AND CheckOutDate;

    SELECT MaxPeople INTO max_people
    FROM Room
    WHERE RoomID = NEW.RoomID
    FOR UPDATE;

    IF people_count > max_people THEN
        RAISE EXCEPTION 'Cannot add more students to Room %: MaxPeople (%) exceeded', NEW.RoomID, max_people;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS enforce_max_people ON Rental;
CREATE TRIGGER enforce_max_people
BEFORE INSERT ON Rental
FOR EACH ROW
EXECUTE FUNCTION check_max_people();