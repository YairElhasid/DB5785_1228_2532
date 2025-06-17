DO $$
DECLARE
    ref refcursor;
    rec RECORD;
    table_rec RECORD;
    student_id INTEGER := 1;
    emp_id INTEGER := 1;
    manager_id INTEGER := 2;
    room_id INTEGER := 4;
    year INTEGER := 2025;
    month INTEGER := 6;
    new_lease_id INTEGER := (SELECT COALESCE(MAX(leaseid), 0) + 1 FROM lease);
    new_request_id INTEGER := (SELECT COALESCE(MAX(requestid), 0) + 1 FROM maintenance_request);
BEGIN
    -- Functions
    BEGIN
        FOR table_rec IN SELECT * FROM calculate_annual_revenue_and_discounts(year)
        LOOP
            RAISE NOTICE 'Function calculate_annual_revenue_and_discounts: Revenue: %, Discount Cost: %', table_rec.total_revenue, table_rec.total_discount_cost;
        END LOOP;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Error in calculate_annual_revenue_and_discounts: %', SQLERRM;
    END;

    BEGIN
        ref := employee_attendance_summary(emp_id, month, year);
        LOOP
            FETCH ref INTO rec;
            EXIT WHEN NOT FOUND;
            RAISE NOTICE 'Function employee_attendance_summary: Date %, Hours %', rec.log_date, rec.hours_worked;
        END LOOP;
        CLOSE ref;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Error in employee_attendance_summary: %', SQLERRM;
    END;

    BEGIN
        FOR table_rec IN SELECT * FROM count_maintenance_by_priority()
        LOOP
            RAISE NOTICE 'Function count_maintenance_by_priority: Priority %, Count %', table_rec.priority, table_rec.request_count;
        END LOOP;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Error in count_maintenance_by_priority: %', SQLERRM;
    END;

    -- Procedures
    BEGIN
        CALL reassign_leases_to_manager(1, manager_id);
        RAISE NOTICE 'Procedure reassign_leases_to_manager executed';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Error in reassign_leases_to_manager: %', SQLERRM;
    END;

    BEGIN
        CALL assign_rooms_to_students(student_id, room_id);
        RAISE NOTICE 'Procedure assign_rooms_to_students executed';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Error in assign_rooms_to_students: %', SQLERRM;
    END;

    BEGIN
        CALL extend_contract_period(12);
        RAISE NOTICE 'Procedure extend_contract_period executed';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Error in extend_contract_period: %', SQLERRM;
    END;

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in main_program_1: %', SQLERRM;
END;
$$;