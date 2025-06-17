DO $$
DECLARE
    ref refcursor;
    rec RECORD;
    student_id INTEGER := 1;
    emp_id INTEGER := 1;
    dept_id INTEGER := 1;
    date_param DATE := CURRENT_DATE;
    building_id INTEGER := 1;
    apartment_id INTEGER := 1;
    room_id INTEGER := 1;
BEGIN
    -- Functions
    BEGIN
        ref := student_rental_history(student_id);
        LOOP
            FETCH ref INTO rec;
            EXIT WHEN NOT FOUND;
            RAISE NOTICE 'Function student_rental_history: Room %, Check-in %', rec.roomid, rec.checkindate;
        END LOOP;
        CLOSE ref;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Error in student_rental_history: %', SQLERRM;
    END;

    BEGIN
        ref := employee_attendance_violations(date_param);
        LOOP
            FETCH ref INTO rec;
            EXIT WHEN NOT FOUND;
            RAISE NOTICE 'Function employee_attendance_violations: Emp ID %, Name %', rec.emp_id, rec.emp_name;
        END LOOP;
        CLOSE ref;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Error in employee_attendance_violations: %', SQLERRM;
    END;

    -- Procedures
    BEGIN
        CALL process_pending_leave_requests();
        RAISE NOTICE 'Procedure process_pending_leave_requests executed';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Error in process_pending_leave_requests: %', SQLERRM;
    END;

    BEGIN
        CALL archive_old_rentals();
        RAISE NOTICE 'Procedure archive_old_rentals executed';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Error in archive_old_rentals: %', SQLERRM;
    END;

    BEGIN
        CALL assign_maintenance_to_team(dept_id);
        RAISE NOTICE 'Procedure assign_maintenance_to_team executed';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Error in assign_maintenance_to_team: %', SQLERRM;
    END;

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in main_program_2: %', SQLERRM;
END;
$$;