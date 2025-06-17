-- Procedure 1: Reassign leases to a new manager
CREATE OR REPLACE PROCEDURE reassign_leases_to_manager(p_old_manager_id INTEGER, p_new_manager_id INTEGER)
LANGUAGE plpgsql AS $$
DECLARE
    lease_rec RECORD;
BEGIN
    FOR lease_rec IN
        SELECT leaseid FROM lease WHERE managerid = p_old_manager_id
    LOOP
        UPDATE lease
        SET managerid = p_new_manager_id
        WHERE leaseid = lease_rec.leaseid;
    END LOOP;

    IF NOT FOUND THEN
        RAISE NOTICE 'No leases found for manager %', p_old_manager_id;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in reassign_leases_to_manager: %', SQLERRM;
END;
$$;

-- Procedure 2: Assign rooms to students
CREATE OR REPLACE PROCEDURE assign_rooms_to_students(p_student_id INTEGER, p_room_id INTEGER)
LANGUAGE plpgsql AS $$
DECLARE
    lease_id INTEGER;
    manager_id INTEGER;
BEGIN
    SELECT managerid INTO manager_id
    FROM managerfullprofile
    ORDER BY random()
    LIMIT 1;

    IF NOT FOUND THEN
        RAISE NOTICE 'No managers found in the employee table.';
        RETURN;
    END IF;

    SELECT COALESCE(MAX(leaseid), 0) + 1 INTO lease_id
    FROM lease;

    INSERT INTO lease (leaseid, contractdate, discountpercent, managerid)
    VALUES (lease_id, CURRENT_DATE, 2.5, manager_id);

    INSERT INTO rental (studentid, roomid, leaseid, checkindate, checkoutdate)
    VALUES (p_student_id, p_room_id, lease_id, CURRENT_DATE, CURRENT_DATE + INTERVAL '1 year');

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in assign_rooms_to_students: %', SQLERRM;
END;
$$;

-- Procedure 3: Extend contract period
CREATE OR REPLACE PROCEDURE extend_contract_period(p_months INTEGER)
LANGUAGE plpgsql AS $$
DECLARE
    contract_rec RECORD;
BEGIN
    FOR contract_rec IN
        SELECT contract_id
        FROM contract
        WHERE end_date < CURRENT_DATE + INTERVAL '3 months'
    LOOP
        UPDATE contract
        SET end_date = end_date + (p_months || ' months')::INTERVAL
        WHERE contract_id = contract_rec.contract_id;
    END LOOP;

    IF NOT FOUND THEN
        RAISE NOTICE 'No contracts near expiry';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in extend_contract_period: %', SQLERRM;
END;
$$;

-- Procedure 4: Process pending leave requests
CREATE OR REPLACE PROCEDURE process_pending_leave_requests()
LANGUAGE plpgsql AS $$
DECLARE
    leave_rec RECORD;
    attendance_count INTEGER;
BEGIN
    FOR leave_rec IN
        SELECT lr.leave_id, lr.emp_id
        FROM leave_requests lr
        JOIN dorm_management dm ON lr.emp_id = dm.managerid
        WHERE lr.status = 'Pending'
    LOOP
        SELECT COUNT(*) INTO attendance_count
        FROM attendance_log al
        WHERE al.employee_id = leave_rec.emp_id
        AND al.log_date >= CURRENT_DATE - INTERVAL '1 month'
        AND al.check_in_time IS NOT NULL;

        IF attendance_count >= 2 THEN
            UPDATE leave_requests
            SET status = 'Approved'
            WHERE leave_id = leave_rec.leave_id;
        ELSE
            UPDATE leave_requests
            SET status = 'Rejected'
            WHERE leave_id = leave_rec.leave_id;
        END IF;
    END LOOP;

    IF NOT FOUND THEN
        RAISE NOTICE 'No pending leave requests';
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in process_pending_leave_requests: %', SQLERRM;
END;
$$;

-- Procedure 5: Archive old rentals
CREATE OR REPLACE PROCEDURE archive_old_rentals()
LANGUAGE plpgsql AS $$
DECLARE
    rental_rec RECORD;
BEGIN
    FOR rental_rec IN
        SELECT leaseid
        FROM rental
        WHERE checkoutdate < CURRENT_DATE - INTERVAL '2 years'
    LOOP
        INSERT INTO rental_archive
        SELECT * FROM rental WHERE leaseid = rental_rec.leaseid;

        DELETE FROM rental WHERE leaseid = rental_rec.leaseid;
    END LOOP;

    IF NOT FOUND THEN
        RAISE NOTICE 'No old rentals to archive';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in archive_old_rentals: %', SQLERRM;
END;
$$;

-- Procedure 7: Assign maintenance to team
CREATE OR REPLACE PROCEDURE assign_maintenance_to_team(p_department_id INTEGER)
LANGUAGE plpgsql AS $$
DECLARE
    maint_rec RECORD;
    emp_rec RECORD;
BEGIN
    SELECT emp_id INTO emp_rec
    FROM employeewithdeptposcontract
    WHERE department_id = p_department_id
    LIMIT 1;

    IF NOT FOUND THEN
        RAISE NOTICE 'No employees found in department %', p_department_id;
        RETURN;
    END IF;

    FOR maint_rec IN
        SELECT requestid
        FROM maintenance_request
        WHERE resolveddate IS NULL
    LOOP
        UPDATE maintenance_request
        SET managerid = emp_rec.emp_id
        WHERE requestid = maint_rec.requestid;
    END LOOP;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in assign_maintenance_to_team: %', SQLERRM;
END;
$$;