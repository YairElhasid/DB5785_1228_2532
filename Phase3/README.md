# University Management Database - Stage 3 Report

## Table of Contents
- [Introduction](#introduction)
- [Database Diagrams and Integration Steps](#database-diagrams-and-integration-steps)
  - [1. DSD of the New Department (HR)](#1-dsd-of-the-new-department-hr)
  - [2. ERD of the New Department (HR)](#2-erd-of-the-new-department-hr)
  - [3. Combined ERD (After Integration)](#3-combined-erd-after-integration)
  - [4. DSD After Integration](#4-dsd-after-integration)
  - [5. Database Modification Commands (Integrate.sql)](#5-database-modification-commands-integratesql)
  - [6. Views and Queries (Views.sql)](#6-views-and-queries-viewssql)
  - [7. Updated Backup File](#7-updated-backup-file)

## Introduction
We have received the university's HR database, and we are integrating this database with our existing Dormitory Management database. This process is designed to unify employee and dormitory management data, enabling seamless operations across both systems. The integration leverages shared keys, as every dormitory manager is also an employee, ensuring data consistency and accessibility. Adjustments and modifications are made to our Dormitory Management database to accommodate the imported HR data.

## Database Diagrams and Integration Steps

### 1. DSD of the New Department (HR)
The Data Structure Diagram (DSD) of the new department (HR) before integration.
- Image: ![DSD Other](images/DSDother.png)

### 2. ERD of the New Department (HR)
The Entity-Relationship Diagram (ERD) of the new department (HR) before integration.
- Image: ![ERD Other](images/ERDother.png)

### 3. Combined ERD (After Integration)
The combined ERD showing the integrated structure of both the Dormitory Management and HR databases.
- Image: ![Combined ERD](images/ERD_COMBINDE.png)

### 4. DSD After Integration
The finalized DSD after the integration of the HR database into the Dormitory Management database.
- Image: ![DSD Final](images/DSD_final.png)

### 5. Database Modification Commands (Integrate.sql)
Below are the commands executed to integrate the HR database into our Dormitory Management database, as detailed in the `Integrate.sql` file:

#### Integration of Foreign Tables
Foreign tables from the HR database were imported into our Dormitory Management database using PostgreSQL's `IMPORT FOREIGN SCHEMA` command. This was done via a server connection (`otherdatabase_server`) to make the HR tables accessible locally. 
The foreign tables are **displayed** in our database, **but are not physically copied to our database.** They are displayed transparently from the remote database that we do not own. Any changes made to this database will be reflected in the foreign tables, the view is what unites them based on primary keys, which each database enforces for its database. 
This results in a view that can be worked with - and queries that combine data from both databases.

```sql
IMPORT FOREIGN SCHEMA public
FROM SERVER otherdatabase_server
INTO public;
```

- **Image**: Remote Server Returning Foreign Tables
  - ![Foreign Tables](images/forgienTabels.png)

#### Removal of Redundant Column
The `fullname` column in the `dorm_management` table of our Dormitory Management database was removed, as manager names are inherited from the `employee_remote` table (imported from HR) via the `ManagerFullProfile` view. This avoids data duplication and ensures consistency by linking records through the shared `emp_id`/`managerid` keys.

```sql
ALTER TABLE public.dorm_management
DROP COLUMN fullname;
```

#### Standardization of Manager Email Addresses
Manager email addresses in the `dorm_management` table of our Dormitory Management database were updated to a standardized format (`lowercase(firstname.lastname.empid@staff.university.ac.il)`) using the employee names from the imported `employee_remote` table. 
For example, an employee named "John Doe" with `emp_id` 123 gets the email `john.doe123@staff.university.ac.il`.

```sql
UPDATE public.dorm_management d
SET email = 
    LOWER(
        split_part(e.emp_name, ' ', 1) || '.' || split_part(e.emp_name, ' ', 2) || e.emp_id
    ) || '@staff.university.ac.il'
FROM public.employee_remote e
WHERE d.managerid = e.emp_id;
```

#### Integration Decisions and Explanation
- **Foreign Keys and Constraints**: No additional foreign keys or constraints were added. Each database retains its own constraints, and the foreign tables ensure data consistency between the Dormitory Management and HR databases. 
Changes in the HR database are automatically reflected in the linked foreign tables in our Dormitory Management database, and vice versa.
This synchronization is achieved because every dormitory manager is also an employee, allowing the views to integrate data using shared keys (`emp_id` and `managerid`).
- **Purpose of Integration**: The integration enables unified access to employee data from HR and dormitory management data in our system, with views like `ManagerFullProfile` linking the two by matching managers to their employee records.

#### Explanation of the Process
The integration process began by importing foreign tables from the HR database into our Dormitory Management database using `IMPORT FOREIGN SCHEMA`. This allowed us to work with HR data within our system. We then removed the redundant `fullname` column from `dorm_management`, as manager names are already available in `employee_remote` and can be accessed via the `ManagerFullProfile` view. Finally, we standardized manager email addresses in our database to ensure consistent communication formats across systems. The shared keys (`emp_id` and `managerid`) enable seamless data integration without additional constraints, maintaining data integrity through the existing constraints of each database.

### 6. Views and Queries (Views.sql)
Below are the views and queries used to support HR operations within our Dormitory Management database, including David’s [The dedicated manager we met in the previous stage:) ] planning for a recognition ceremony and a management conference.

#### View: `EmployeeWithDeptPosContract`
- **Description**: This view integrates employee data with their department, position, and contract details.
It provides a comprehensive profile of employees, including their department name  and  location, position title and  level, and  contract details (start  date, end  date, and salary).
Useful for HR to track employee roles, locations, and  contract statuses.

- **Story**: David relies on this view to organize and integrate employee data from the imported HR system into our Dormitory Management database. It combines employee records with their department, position, and contract details, creating a single, reliable source of information. It helps David streamline his planning by providing a clear picture of each employee’s role, location, and contract status, which is essential for identifying candidates for the recognition ceremony and ensuring contract renewals are handled before the management conference.

```sql
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
```

  - **Image**: ![EmployeeWithDeptPosContract](images/EmployeeWithDeptPosContract.png)

#### Query: Employees Absent Today
- **Description**: This query calculates and returns a table of employees who did not show up for work today (May 20, 2025). It checks attendance records and identifies employees with no log entry for the current date.
- **Story**: David uses this query to identify employees absent on May 20, 2025, which is critical as he prepares for the recognition ceremony. By knowing who is not present, he can follow up with them to ensure they receive their invitations or check on their availability. This helps him avoid missing key contributors to the dormitory’s success, ensuring a fair and inclusive ceremony.

```sql
SELECT 
    e.Emp_ID,
    e.Emp_Name,
    e.department_name,
    e.position_title
FROM EmployeeWithDeptPosContract e
LEFT JOIN Attendance_Log_remote a ON e.Emp_ID = a.employee_id AND a.log_date = CURRENT_DATE
WHERE a.log_id IS NULL;
```

- **Output**:
  - **Image**: ![Employees Absent Today](images/Query_Employees_Absent_Today.png)

#### Query: Employees with Contracts Expiring in 90 Days
- **Description**: This query calculates and returns a table of employees whose contracts will end within the next 90 days (May 20, 2025, to August 18, 2025). It filters employees based on their contract end dates and sorts them by expiration date for prioritization.
- **Story**: David runs this query to identify employees whose contracts are nearing their end, a key concern as he plans the management conference. Knowing who might leave soon allows him to prioritize contract renewals, ensuring that experienced staff, especially those involved in lease sales, can attend the conference and learn new strategies, maintaining the university’s dormitory occupancy rates - or for the purpose of extending their employment.

```sql
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
```

- **Output**:
  - **Image**: ![Contracts Expiring in 90 Days](images/Query%20Employees%20with%20Contracts%20Expiring%20in%2090%20Days.png)

#### View: `ManagerFullProfile`
- **Description**: This view integrates manager data by combining employee information from the HR database with dormitory management details from our system. It organizes data about managers’ departments, positions, and contact information, providing a unified profile. It enables integration between the HR and dormitory systems by linking managers to their employee records.
- **Story**: David uses the `ManagerFullProfile` view to organize and integrate data about managers from the HR database into our Dormitory Management database. This view consolidates managers’ roles, contact details, and hire dates into a single source, making it easier for him to identify candidates for the recognition ceremony and invite them to the management conference, where they can share their expertise and learn new sales techniques.
This view offers David and other managers a comprehensive perspective of the unified database. It serves as an integration bridge between the two databases, enabling seamless querying and analysis across both databases.


```sql
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
```

  - **Image**: ![ManagerFullProfile](images/View%20ManagerFullProfile.png)

#### Query: Experienced Managers (Over 5 Years, Senior Level)
- **Description**: This query calculates and returns a table of senior managers (position level > 2) with over 5 years of service (hired before May 20, 2020). It provides their names, phone numbers, emails, and years in role, useful for contacting long-serving managers.
- **Story**: David uses this query to find senior managers with over 5 years of tenure, whom he wants to honor at the recognition ceremony. The returned phone numbers and emails allow him to personally invite these experienced leaders, whose long service has contributed to the dormitory’s success. Their presence at the ceremony will inspire others, and their experience will be valuable at the management conference.

```sql
SELECT 
    managername,
    managerphone,
    manageremail,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, managerhiredate)) AS years_in_role
FROM public.managerfullprofile
WHERE 
    positionlevel > 2
    AND managerhiredate <= CURRENT_DATE - INTERVAL '5 years';
```

- **Output**:
  - **Image**: ![Experienced Managers](images/Query%20Experienced%20Managers.png)

#### Query: Manager with the Most Lease Sales
- **Description**: This query calculates and returns the manager(s) who have signed the highest number of leases. It counts leases per manager and identifies those with the maximum total, returning their ID, name, hire date, phone, email, and lease count.
- **Story**: David runs this query to identify the top-performing manager(s) in lease sales, a key metric for the dormitory’s occupancy success. The query returns their contact details (phone and email), which David uses to invite them to the recognition ceremony as honorees. Additionally, he plans to feature them as speakers at the management conference, where they can share their sales strategies with peers, enhancing the university’s overall performance.

```sql
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
```

- **Output**:
  - **Image**: ![Manager with Most Lease Sales](images/Query%20Manager%20with%20the%20Most%20Lease%20Sales.png)

### 7. Updated Backup File
- **Backup File**: An updated backup of the integrated Dormitory Management database is available.
  - [Backup__3_21_05_2025](Backups/Backup__3_21_05_2025)

- **Scripts**:
  - [Integrate.sql](Integrate.sql)
  - [Views.sql](Views.sql)
- All images are stored in the `images` directory.