-- We imported the new department's database into other database!
-- We took all the tables and made them accessible by creating foreign tables in our database
-- and copied these foreign tables into our database so we can apply constraints and modifications as needed for integration,
-- since PostgreSQL does not allow constraints on foreign tables.
-- We imported foreign tables into our database.
IMPORT FOREIGN SCHEMA public
FROM SERVER otherdatabase_server
INTO public;

-- As part of integration decisions, we concluded that there is no need for a name field for managers since it exists in the employee names.
-- Managers inherit from employees.
ALTER TABLE public.dorm_management
DROP COLUMN fullname;

-- Updated the emails of managers based on their names as they appear in the employee table.
-- All emails in the university follow the format based on the employee name.
UPDATE public.dorm_management d
SET email = 
    LOWER(
        split_part(e.emp_name, ' ', 1) || '.' || split_part(e.emp_name, ' ', 2)
    ) || '@staff.university.ac.il'
FROM public.employee_remote e
WHERE d.managerid = e.emp_id;

-- The position names did not match their content - an error in the database we received.
-- We swapped the values of name and location to correct this.
UPDATE public.department_local
SET 
    name = location,
    location = name;

-- Copied all foreign tables into our database with a 'local' suffix to distinguish them from the foreign (remote) tables.
DO $$
DECLARE
    r RECORD;
    src_table TEXT;
    dest_table TEXT;
BEGIN
    FOR r IN
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name LIKE '%_remote'
    LOOP
        src_table := format('public.%I', r.table_name);
        dest_table := replace(r.table_name, '_remote', '_local');

        RAISE NOTICE 'Copying from % to %', src_table, dest_table;

        EXECUTE format(
            'CREATE TABLE public.%I AS TABLE %s;',
            dest_table,
            src_table
        );
    END LOOP;
END $$;

-- Now we will add primary key constraints to the tables we imported.
BEGIN;

ALTER TABLE public.attendance_log_local
ADD CONSTRAINT pk_attendance_log PRIMARY KEY (log_id);

ALTER TABLE public.contract_local
ADD CONSTRAINT pk_contract PRIMARY KEY (contract_id);

ALTER TABLE public.department_local
ADD CONSTRAINT pk_department PRIMARY KEY (department_id);

ALTER TABLE public.employee_local
ADD CONSTRAINT pk_employee PRIMARY KEY (emp_id);

ALTER TABLE public.leave_requests_local
ADD CONSTRAINT pk_leave_requests PRIMARY KEY (leave_id);

ALTER TABLE public.position_local
ADD CONSTRAINT pk_position PRIMARY KEY (position_id);

COMMIT;

-- We discovered a discrepancy in the database we received.
-- There should be a foreign key to a position ID that does not exist.
-- We decided to add two new positions here.
BEGIN;

INSERT INTO public.position_local (position_id, title, level)
VALUES 
    (0, 'Unpaid Leave', 1),
    (-1, 'Subject to Termination – No Longer in Role', 2)
ON CONFLICT (position_id) DO NOTHING;

COMMIT;

-- Verify that the insertion was successful.
SELECT *
FROM public.position_local
WHERE position_id IN (0, -1);

-- dding general constraints

-- Add Foreign Key Constraints to Tables
-- Step 1: Validate Data Before Adding FOREIGN KEY Constraints
-- Check for contract_local.emp_id
SELECT emp_id
FROM public.contract_local
WHERE emp_id IS NOT NULL AND emp_id NOT IN (SELECT emp_id FROM public.employee_local);

-- Check for attendance_log_local.employee_id (corrected column name)
SELECT employee_id
FROM public.attendance_log_local
WHERE employee_id IS NOT NULL AND employee_id NOT IN (SELECT emp_id FROM public.employee_local);

-- Check for leave_requests_local.emp_id
SELECT emp_id
FROM public.leave_requests_local
WHERE emp_id IS NOT NULL AND emp_id NOT IN (SELECT emp_id FROM public.employee_local);

-- Check for employee_local.position_id
SELECT position_id
FROM public.employee_local
WHERE position_id IS NOT NULL AND position_id NOT IN (SELECT Position_ID FROM public.position_local);

-- Check for employee_local.department_id
SELECT department_id
FROM public.employee_local
WHERE department_id IS NOT NULL AND department_id NOT IN (SELECT Department_ID FROM public.department_local);

-- Check for dorm_management.emp_id (previously renamed from managerid)
SELECT managerid
FROM public.dorm_management
WHERE managerid IS NOT NULL AND managerid NOT IN (SELECT emp_id FROM public.employee_local);

-- Check for building.emp_id (previously renamed from managerid)
SELECT managerid
FROM public.building
WHERE managerid IS NOT NULL AND managerid NOT IN (SELECT emp_id FROM public.employee_local);

-- Check for lease.emp_id (previously renamed from managerid)
SELECT managerid
FROM public.lease
WHERE managerid IS NOT NULL AND managerid NOT IN (SELECT emp_id FROM public.employee_local);

-- Check for maintenance_request.emp_id (previously renamed from managerid)
SELECT managerid
FROM public.maintenance_request
WHERE managerid IS NOT NULL AND managerid NOT IN (SELECT emp_id FROM public.employee_local);

-- Step 2: Add FOREIGN KEY Constraints
BEGIN;

-- In contract_local: Foreign key emp_id referencing employee_local
ALTER TABLE public.contract_local
ADD CONSTRAINT fk_contract_employee FOREIGN KEY (emp_id) REFERENCES public.employee_local (emp_id) ON DELETE CASCADE ON UPDATE CASCADE;

-- In attendance_log_local: Foreign key employee_id referencing employee_local (corrected column name)
ALTER TABLE public.attendance_log_local
ADD CONSTRAINT fk_attendance_employee FOREIGN KEY (employee_id) REFERENCES public.employee_local (emp_id) ON DELETE CASCADE ON UPDATE CASCADE;

-- In leave_requests_local: Foreign key emp_id referencing employee_local
ALTER TABLE public.leave_requests_local
ADD CONSTRAINT fk_leave_employee FOREIGN KEY (emp_id) REFERENCES public.employee_local (emp_id) ON DELETE CASCADE ON UPDATE CASCADE;

-- In employee_local: Foreign keys position_id and department_id
ALTER TABLE public.employee_local
ADD CONSTRAINT fk_employee_position FOREIGN KEY (position_id) REFERENCES public.position_local (position_id) ON DELETE SET NULL ON UPDATE CASCADE,
ADD CONSTRAINT fk_employee_department FOREIGN KEY (department_id) REFERENCES public.department_local (department_id) ON DELETE SET NULL ON UPDATE CASCADE;

-- In dorm_management: Foreign key emp_id referencing employee_local (previously renamed from managerid)
ALTER TABLE public.dorm_management
ADD CONSTRAINT fk_dorm_management_employee FOREIGN KEY (managerid) REFERENCES public.employee_local (emp_id) ON DELETE CASCADE ON UPDATE CASCADE;

-- In building: Foreign key emp_id referencing employee_local (previously renamed from managerid, already defined but ensuring consistency)
ALTER TABLE public.building
ADD CONSTRAINT fk_building_employee FOREIGN KEY (managerid) REFERENCES public.employee_local (emp_id) ON DELETE CASCADE ON UPDATE CASCADE;

-- In lease: Foreign key emp_id referencing employee_local (previously renamed from managerid, already defined but ensuring consistency)
ALTER TABLE public.lease
ADD CONSTRAINT fk_lease_employee FOREIGN KEY (managerid) REFERENCES public.employee_local (emp_id) ON DELETE CASCADE ON UPDATE CASCADE;

-- In maintenance_request: Foreign key emp_id referencing employee_local (previously renamed from managerid, already defined but ensuring consistency)
ALTER TABLE public.maintenance_request
ADD CONSTRAINT fk_maintenance_employee FOREIGN KEY (managerid) REFERENCES public.employee_local (emp_id) ON DELETE CASCADE ON UPDATE CASCADE;

COMMIT;

-- Verify foreign key constraint
-- Insert a manager with manager_id 450 into dorm_management - for testing
BEGIN;

INSERT INTO public.dorm_management (managerid, PhoneNumber, Email, hiredate)
VALUES 
    (450, '+972 53-452-2668', 'manager450@example.com', '2025-05-20 01:10:00');
	-- EROOR! 

COMMIT;

-- Verify the insertion
SELECT * FROM public.dorm_management WHERE managerid = 450;

-- Adding NOT NULL constraints to all fields of the new tables
-- contract_local
ALTER TABLE public.contract_local ALTER COLUMN contract_id SET NOT NULL;
ALTER TABLE public.contract_local ALTER COLUMN emp_id SET NOT NULL;
ALTER TABLE public.contract_local ALTER COLUMN start_date SET NOT NULL;
ALTER TABLE public.contract_local ALTER COLUMN end_date SET NOT NULL;
ALTER TABLE public.contract_local ALTER COLUMN salary SET NOT NULL;

-- attendance_log_local
ALTER TABLE public.attendance_log_local ALTER COLUMN log_id SET NOT NULL;
ALTER TABLE public.attendance_log_local ALTER COLUMN employee_id SET NOT NULL;
ALTER TABLE public.attendance_log_local ALTER COLUMN log_date SET NOT NULL;
ALTER TABLE public.attendance_log_local ALTER COLUMN check_in_time SET NOT NULL;
ALTER TABLE public.attendance_log_local ALTER COLUMN check_out_time SET NOT NULL;

-- department_local
ALTER TABLE public.department_local ALTER COLUMN department_id SET NOT NULL;
ALTER TABLE public.department_local ALTER COLUMN location SET NOT NULL;
ALTER TABLE public.department_local ALTER COLUMN name SET NOT NULL;

-- employee_local
ALTER TABLE public.employee_local ALTER COLUMN emp_id SET NOT NULL;
ALTER TABLE public.employee_local ALTER COLUMN emp_name SET NOT NULL;
ALTER TABLE public.employee_local ALTER COLUMN department_id SET NOT NULL;
ALTER TABLE public.employee_local ALTER COLUMN position_id SET NOT NULL;

-- leave_requests_local
ALTER TABLE public.leave_requests_local ALTER COLUMN leave_id SET NOT NULL;
ALTER TABLE public.leave_requests_local ALTER COLUMN emp_id SET NOT NULL;
ALTER TABLE public.leave_requests_local ALTER COLUMN start_date SET NOT NULL;
ALTER TABLE public.leave_requests_local ALTER COLUMN end_date SET NOT NULL;
ALTER TABLE public.leave_requests_local ALTER COLUMN status SET NOT NULL;

-- position_local
ALTER TABLE public.position_local ALTER COLUMN position_id SET NOT NULL;
ALTER TABLE public.position_local ALTER COLUMN title SET NOT NULL;
ALTER TABLE public.position_local ALTER COLUMN level SET NOT NULL;