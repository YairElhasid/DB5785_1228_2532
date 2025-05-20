-- First View: ManagerEmployeeContractProfile
-- This view integrates data from the employee_local, dorm_management, 
-- and contract_local tables to provide a comprehensive profile of managers. 
-- It includes their employee details, dorm management information, and employment contract details.

-- Purpose: The view exists to support managing all university managers by integrating HR data 
-- (employee details and contracts) with dormitory management data,
-- ensuring a unified perspective for overseeing manager performance, contract status, and departmental alignment.
CREATE VIEW public.ManagerEmployeeContractProfile AS
SELECT 
    e.emp_id AS employee_id,
    e.emp_name AS EmployeeName,
    e.department_id,
    e.position_id,
    p.title AS PositionTitle,
    d.name AS DepartmentName,
    dm.phonenumber AS ManagerPhone,
    dm.email AS ManagerEmail,
    dm.hiredate AS ManagerHireDate,
    c.contract_id,
    c.start_date AS ContractStartDate,
    c.end_date AS ContractEndDate,
    c.salary AS ContractSalary
FROM public.employee_local e
JOIN public.dorm_management dm ON e.emp_id = dm.managerid
JOIN public.contract_local c ON e.emp_id = c.emp_id
LEFT JOIN public.position_local p ON e.position_id = p.position_id
LEFT JOIN public.department_local d ON e.department_id = d.department_id;

-- First Query on ManagerEmployeeContractProfile

-- David wanted to ensure that all managers overseeing dorms are under active contracts to avoid 
-- operational disruptions. 
-- He plans to recognize those with long-term commitment by organizing a university-wide appreciation event.

-- This query returns managers who have active contracts as of May 20, 2025, [TODAY]
-- including their employee ID, name, position, department, hire date, and contract dates, sorted by name.
SELECT 
    employee_id,
    EmployeeName,
    PositionTitle,
    DepartmentName,
    ManagerHireDate,
    ContractStartDate,
    ContractEndDate
FROM public.ManagerEmployeeContractProfile
WHERE ContractStartDate <= '2025-05-20'
  AND (ContractEndDate IS NULL OR ContractEndDate >= '2025-05-20') 
  ORDER BY EmployeeName;

-- Second Query on ManagerEmployeeContractProfile

-- David identified a need to retain top-performing managers after a recent staff turnover. 
-- He decided to offer promotions to managers earning above 15,000, as they likely have significant experience 
-- and impact.

-- This query returns managers earning a salary above 15,000, including their employee ID, name, 
-- position, department, hire date, and salary, sorted by salary in descending order.
SELECT 
    employee_id,
    EmployeeName,
    PositionTitle,
    DepartmentName,
    ManagerHireDate,
    ContractSalary
FROM public.ManagerEmployeeContractProfile
WHERE ContractSalary > 15000
ORDER BY ContractSalary DESC;

-- Second View: RentalLeaseEmployeeContract
-- Description: This view connects rental and lease data from the dormitory system with employee contract details, 
-- focusing on managers overseeing student leases. It includes rental details, lease terms, 
-- and the manager’s contract information.

-- Purpose: The view facilitates David’s oversight of lease management by integrating dormitory rental data 
-- with HR contract data, 
-- ensuring managers handling student leases are fairly compensated and aligned with university policies.
CREATE VIEW public.RentalLeaseEmployeeContract AS
SELECT 
    r.studentid,
    r.roomid,
    r.leaseid,
    r.checkindate,
    r.checkoutdate,
    l.contractdate AS LeaseContractDate,
    l.discountpercent,
    l.managerid,
    e.position_id,
    p.title AS PositionTitle,
    e.department_id,
    d.name AS DepartmentName,
    c.contract_id,
    c.start_date AS EmployeeContractStartDate,
    c.end_date AS EmployeeContractEndDate,
    c.salary AS EmployeeContractSalary
FROM public.rental r
JOIN public.lease l ON r.leaseid = l.leaseid
JOIN public.employee_local e ON l.managerid = e.emp_id
JOIN public.contract_local c ON e.emp_id = c.emp_id
LEFT JOIN public.position_local p ON e.position_id = p.position_id
LEFT JOIN public.department_local d ON e.department_id = d.department_id;

-- First Query on RentalLeaseEmployeeContract

-- David discovered that some managers were offering excessive discounts on student leases,
-- risking financial losses.
-- He decided to investigate discounts above 17% from non-authorized departments to enforce stricter oversight.

-- This query returns lease details for leases with discounts above 17% 
-- offered by managers not in Sales, Marketing, or Finance departments, 
-- including department ID, department name, lease ID, discount percentage, contract date, and position title, 
-- sorted by discount percentage in descending order.
SELECT 
    department_id,
    DepartmentName,
    leaseid,
    discountpercent,
    LeaseContractDate,
    PositionTitle
FROM public.RentalLeaseEmployeeContract
WHERE discountpercent > 17
  AND DepartmentName NOT IN ('Sales', 'Marketing', 'Finance')
ORDER BY discountpercent DESC;

-- Second Query on RentalLeaseEmployeeContract

-- David wanted to boost morale by launching a bonus program for managers who signed at least 5 leases
-- but earn 17,000 or less,
-- recognizing their dedication to student housing.

-- This query returns managers who have signed at least 5 leases and earn a salary of 17,000 or less,
-- including their manager ID, lease count, salary, and department name, sorted by lease count in descending order.
SELECT
    managerid,
    COUNT(leaseid) AS LeaseCount,
    EmployeeContractSalary,
    DepartmentName
FROM public.RentalLeaseEmployeeContract
GROUP BY EmployeeContractSalary, DepartmentName, managerid
HAVING COUNT(leaseid) >= 5
  AND EmployeeContractSalary <= 17000
ORDER BY LeaseCount DESC;