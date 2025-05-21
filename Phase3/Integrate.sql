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
-- This update statement standardizes email addresses for managers in the dorm_management table.
-- It creates emails in the format: lowercase(firstname.lastname.empid@staff.university.ac.il).
-- For example, if an employee named "John Doe" has emp_id 123, their email becomes john.doe123@staff.university.ac.il.
-- It joins employee_remote to get the employee name and ID for managers listed in dorm_management.
UPDATE public.dorm_management d
SET email = 
    LOWER(
        split_part(e.emp_name, ' ', 1) || '.' || split_part(e.emp_name, ' ', 2) || e.emp_id
    ) || '@staff.university.ac.il'
FROM public.employee_remote e
WHERE d.managerid = e.emp_id;
