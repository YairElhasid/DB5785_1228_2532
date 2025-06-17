-- Function 1: Calculate annual revenue and discounts
CREATE OR REPLACE FUNCTION calculate_annual_revenue_and_discounts(p_year INTEGER)
RETURNS TABLE (total_revenue NUMERIC, total_discount_cost NUMERIC) AS $$
DECLARE
    lease_rec RECORD;
    start_date DATE := MAKE_DATE(p_year - 1, 9, 1);
    end_date DATE := MAKE_DATE(p_year, 8, 31);
    base_rental_cost NUMERIC := 1000.0 * 12; -- Annual cost per room
    revenue NUMERIC := 0;
    discount_cost NUMERIC := 0;
BEGIN
    FOR lease_rec IN
        SELECT l.leaseid, l.discountpercent, r.checkindate, r.checkoutdate
        FROM lease l
        JOIN rental r ON l.leaseid = r.leaseid
        WHERE r.checkindate <= end_date AND (r.checkoutdate >= start_date OR r.checkoutdate IS NULL)
    LOOP
        IF lease_rec.discountpercent < 0 OR lease_rec.discountpercent > 100 THEN
            RAISE EXCEPTION 'Invalid discount percent % for lease %', lease_rec.discountpercent, lease_rec.leaseid;
        END IF;

        revenue := revenue + base_rental_cost * (1 - lease_rec.discountpercent / 100);
        discount_cost := discount_cost + base_rental_cost * (lease_rec.discountpercent / 100);
    END LOOP;

    IF revenue = 0 THEN
        RAISE NOTICE 'No leases found for academic year %', p_year;
    END IF;

    RETURN QUERY SELECT ROUND(revenue, 2) AS total_revenue, ROUND(discount_cost, 2) AS total_discount_cost;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in calculate_annual_revenue_and_discounts: %', SQLERRM;
        RETURN QUERY SELECT 0.0::NUMERIC, 0.0::NUMERIC;
END;
$$ LANGUAGE plpgsql;

-- Function 2: Employee attendance summary
CREATE OR REPLACE FUNCTION employee_attendance_summary(p_emp_id INTEGER, p_month INTEGER, p_year INTEGER)
RETURNS refcursor AS $$
DECLARE
    att_cursor CURSOR FOR
        SELECT log_date, check_in_time, check_out_time
        FROM attendance_log
        WHERE employee_id = p_emp_id
        AND EXTRACT(MONTH FROM log_date) = p_month
        AND EXTRACT(YEAR FROM log_date) = p_year;
    att_rec RECORD;
    ref refcursor := 'attendance_cursor';
    total_hours NUMERIC := 0;
BEGIN
    OPEN att_cursor;
    OPEN ref FOR SELECT log_date, check_in_time, check_out_time, 0.0 AS hours_worked FROM attendance_log WHERE 1=0;

    LOOP
        FETCH att_cursor INTO att_rec;
        EXIT WHEN NOT FOUND;

        IF att_rec.check_out_time IS NOT NULL THEN
            total_hours := total_hours + EXTRACT(EPOCH FROM (att_rec.check_out_time - att_rec.check_in_time)) / 3600;
        END IF;

        UPDATE attendance_log
        SET check_out_time = CURRENT_TIME + INTERVAL '1 hour'
        WHERE employee_id = p_emp_id AND log_date = att_rec.log_date AND check_out_time IS NULL;
    END LOOP;

    CLOSE att_cursor;
    CLOSE ref;

    OPEN ref FOR
        SELECT log_date, check_in_time, check_out_time,
               CASE WHEN check_out_time IS NOT NULL
                    THEN EXTRACT(EPOCH FROM (check_out_time - check_in_time)) / 3600
                    ELSE 0
               END AS hours_worked
        FROM attendance_log
        WHERE employee_id = p_emp_id
        AND EXTRACT(MONTH FROM log_date) = p_month
        AND EXTRACT(YEAR FROM log_date) = p_year;

    IF total_hours = 0 THEN
        RAISE NOTICE 'No attendance records for employee % in %/%', p_emp_id, p_month, p_year;
    END IF;

    RETURN ref;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in employee_attendance_summary: %', SQLERRM;
        CLOSE ref;
        OPEN ref FOR SELECT log_date, check_in_time, check_out_time, 0.0 AS hours_worked FROM attendance_log WHERE 1=0;
        RETURN ref;
END;
$$ LANGUAGE plpgsql;

-- Function 3: Count maintenance requests by priority
CREATE OR REPLACE FUNCTION count_maintenance_by_priority()
RETURNS TABLE (priority VARCHAR, request_count INTEGER) AS $$
DECLARE
    maint_rec RECORD;
BEGIN
    FOR maint_rec IN
        SELECT maintenance_request.priority::VARCHAR AS priority, COUNT(*)::INTEGER AS request_count
        FROM maintenance_request
        GROUP BY maintenance_request.priority
    LOOP
        IF maint_rec.request_count = 0 THEN
            RAISE NOTICE 'No requests found for priority %', maint_rec.priority;
            CONTINUE;
        END IF;

        RETURN QUERY SELECT maint_rec.priority, maint_rec.request_count;
    END LOOP;

    IF NOT FOUND THEN
        RAISE NOTICE 'No maintenance requests found';
    END IF;

    RETURN;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in count_maintenance_by_priority: %', SQLERRM;
        RETURN;
END;
$$ LANGUAGE plpgsql;

-- Function 4: Employee attendance violations
CREATE OR REPLACE FUNCTION employee_attendance_violations(p_date DATE)
RETURNS refcursor AS $$
DECLARE
    emp_cursor CURSOR FOR
        SELECT e.emp_id, e.emp_name
        FROM employee e
        WHERE NOT EXISTS (
            SELECT 1 FROM attendance_log al
            WHERE al.employee_id = e.emp_id AND al.log_date = p_date
        );
    emp_rec RECORD;
    ref refcursor := 'attendance_violations_cursor';
BEGIN
    OPEN emp_cursor;
    OPEN ref FOR SELECT emp_id, emp_name FROM employee WHERE 1=0;

    LOOP
        FETCH emp_cursor INTO emp_rec;
        EXIT WHEN NOT FOUND;
    END LOOP;

    CLOSE emp_cursor;
    CLOSE ref;

    OPEN ref FOR
        SELECT e.emp_id, e.emp_name
        FROM employee e
        WHERE NOT EXISTS (
            SELECT 1 FROM attendance_log al
            WHERE al.employee_id = e.emp_id AND al.log_date = p_date
        );

    RETURN ref;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in employee_attendance_violations: %', SQLERRM;
        CLOSE ref;
        OPEN ref FOR SELECT emp_id, emp_name FROM employee WHERE 1=0;
        RETURN ref;
END;
$$ LANGUAGE plpgsql;

-- Function 5: Student rental history
CREATE OR REPLACE FUNCTION student_rental_history(p_studentid INTEGER)
RETURNS refcursor AS $$
DECLARE
    rental_cursor CURSOR FOR
        SELECT r.leaseid, r.roomid, r.checkindate, r.checkoutdate
        FROM rental r
        WHERE r.studentid = p_studentid;
    rental_rec RECORD;
    ref refcursor := 'rental_history_cursor';
BEGIN
    OPEN rental_cursor;
    OPEN ref FOR SELECT leaseid, roomid, checkindate, checkoutdate FROM rental WHERE 1=0;

    LOOP
        FETCH rental_cursor INTO rental_rec;
        EXIT WHEN NOT FOUND;

        IF rental_rec.checkoutdate < rental_rec.checkindate THEN
            RAISE EXCEPTION 'Invalid rental dates for lease %', rental_rec.leaseid;
        END IF;
    END LOOP;

    CLOSE rental_cursor;
    CLOSE ref;

    OPEN ref FOR
        SELECT r.leaseid, r.roomid, r.checkindate, r.checkoutdate
        FROM rental r
        WHERE r.studentid = p_studentid;

    RETURN ref;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in student_rental_history: %', SQLERRM;
        CLOSE ref;
        OPEN ref FOR SELECT leaseid, roomid, checkindate, checkoutdate FROM rental WHERE 1=0;
        RETURN ref;
END;
$$ LANGUAGE plpgsql;