-- View: EmployeeWithDeptPosContract
-- This view integrates employee data with their department, position, and contract details.
-- It provides a comprehensive profile of employees, including their department name and location,
-- position title and level, and contract details (start date, end date, and salary).
-- Useful for HR to track employee roles, locations, and contract statuses.
CREATE OR REPLACE VIEW EmployeeWithDeptPosContract AS
SELECT
    e.Emp_ID,
    e.Emp_Name,
    e.department_id,
    e.position_id,
    d.name AS department_name,
    d.location AS department_location,
    p.title AS position_title,
    p.level AS position_level,
    c.contract_id,
    c.start_date AS contract_start_date,
    c.end_date AS contract_end_date,
    c.salary AS contract_salary
FROM
    Employee_remote e
    JOIN Department_remote d ON e.department_id = d.department_id
    JOIN Position_remote p ON e.position_id = p.position_id
    JOIN Contract_remote c ON e.Emp_ID = c.emp_id;

-- David, relies on the EmployeeWithDeptPosContract view to organize and integrate employee data from various systems.
-- This view combines employee records with their department, position, and contract details, creating a single, reliable source of information.
-- It helps David streamline his planning by providing a clear picture of each employee’s role, location, and contract status, which is essential
-- for identifying candidates for the recognition ceremony and ensuring contract renewals are handled before the management conference.

-- Query: Employees Absent Today
-- This query calculates and returns a table of employees who did not show up for work today.
-- It checks attendance records and identifies employees with no log entry for the current date.
SELECT 
    e.Emp_ID,
    e.Emp_Name,
    e.department_name,
    e.position_title
FROM EmployeeWithDeptPosContract e
LEFT JOIN Attendance_Log_remote a ON e.Emp_ID = a.employee_id AND a.log_date = CURRENT_DATE
WHERE a.log_id IS NULL;

-- David uses this query to identify employees absent today, which is critical as he prepares for the recognition ceremony.
-- By knowing who is not present, he can follow up with them to ensure they receive their invitations or check on their availability.
-- This helps him avoid missing key contributors to the dormitory’s success, ensuring a fair and inclusive ceremony.

-- Query: Employees with Contracts Expiring in 90 Days
-- This query calculates and returns a table of employees whose contracts will end within the next 90 days.
-- It filters employees based on their contract end dates and sorts them by expiration date for prioritization.
SELECT
    Emp_ID,
    Emp_Name,
    position_title,
    contract_start_date,
    contract_end_date,
    contract_salary
FROM EmployeeWithDeptPosContract
WHERE contract_end_date IS NOT NULL
  AND contract_end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '90 days'
ORDER BY contract_end_date ASC;

-- David runs this query to identify employees whose contracts are nearing their end, a key concern as he plans the management conference.
-- Knowing who might leave soon allows him to prioritize contract renewals, ensuring that experienced staff, especially those involved in lease sales,
-- can attend the conference and learn new strategies, maintaining the university’s dormitory occupancy rates.
-- Or of course for the purpose of extending their employment.

-- View: ManagerFullProfile
-- This view integrates manager data by combining employee information with dormitory management details.
-- It organizes data about managers’ departments, positions, and contact information, providing a unified profile.
-- Essential for HR to track managers’ roles and contact them across both HR and dormitory systems.
-- This view also allows for a uniform presentation of all data about the dormitory manager and enables 
-- integration between the parts of the departments that are part of the university.
CREATE OR REPLACE VIEW ManagerFullProfile AS
SELECT 
    e.emp_id AS ManagerID,
    e.emp_name AS ManagerName,
    e.department_id,
    d.name AS DepartmentName,
    d.location AS DepartmentLocation,
    e.position_id,
    p.title AS PositionTitle,
    p.level AS PositionLevel,
    dm.phonenumber AS ManagerPhone,
    dm.email AS ManagerEmail,
    dm.hiredate AS ManagerHireDate
FROM public.employee_remote e
JOIN public.dorm_management dm ON e.emp_id = dm.managerid
LEFT JOIN public.department_remote d ON e.department_id = d.department_id
LEFT JOIN public.position_remote p ON e.position_id = p.position_id;

-- David uses the ManagerFullProfile view to organize and integrate data about managers from both the HR and dormitory management systems.
-- This view consolidates managers’ roles, contact details, and hire dates into a single source, making it easier for him to identify candidates
-- for the recognition ceremony and invite them to the management conference, where they can share their expertise and learn new sales techniques.

-- Query: Experienced Managers (Over 5 Years, Senior Level)
-- This query calculates and returns a table of senior managers (position level > 2) with over 5 years of service.
-- It provides their names, phone numbers, emails, and years in role, useful for contacting long-serving managers.
SELECT 
    managername,
    managerphone,
    manageremail,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, managerhiredate)) AS years_in_role
FROM public.managerfullprofile
WHERE 
    positionlevel > 2
    AND managerhiredate <= CURRENT_DATE - INTERVAL '5 years';

-- David uses this query to find senior managers with over 5 years of tenure, whom he wants to honor at the recognition ceremony.
-- The returned phone numbers and emails allow him to personally invite these experienced leaders, whose long service has contributed to the
-- dormitory’s success. Their presence at the ceremony will inspire others, and their experience will be valuable at the management conference.

-- Query: Manager with the Most Lease Sales
-- This query calculates and returns the manager(s) who have signed the highest number of leases.
-- It counts leases per manager and identifies those with the maximum total, returning their ID, name, hire date, phone, email, and lease count.
SELECT 
    mfp.managerid,
    mfp.managername,
    mfp.managerhiredate,
    mfp.managerphone,
    mfp.manageremail,
    COUNT(l.leaseid) AS total_leases_signed
FROM 
    managerfullprofile mfp
JOIN 
    lease l ON mfp.managerid = l.managerid
GROUP BY 
    mfp.managerid, mfp.managername, mfp.managerhiredate, mfp.managerphone, mfp.manageremail
HAVING 
    COUNT(l.leaseid) = (
        SELECT MAX(lease_count)
        FROM (
            SELECT COUNT(l2.leaseid) AS lease_count
            FROM managerfullprofile mfp2
            JOIN lease l2 ON mfp2.managerid = l2.managerid
            GROUP BY mfp2.managerid
        ) AS sub
    );

-- David runs this query to identify the top-performing manager(s) in lease sales, a key metric for the dormitory’s occupancy success.
-- The query returns their contact details (phone and email), which David uses to invite them to the recognition ceremony as honorees.
-- Additionally, he plans to feature them as speakers at the management conference, where they can share their sales strategies with peers,
-- enhancing the university’s overall performance.