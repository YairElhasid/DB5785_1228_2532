
# Phase 3 Project Documentation - Dormitory Management System

## Table of Contents
- [Overview](#overview)
- [Files Included](#files-included)
- [Integration Decisions and Rationale](#integration-decisions-and-rationale)
- [Summary of Changes](#summary-of-changes)
- [Project Report Phase 3](#project-report-phase-3)
  - [Screenshots of DSD and ERD Diagrams](#screenshots-of-dsd-and-erd-diagrams)
  - [Detailed Integration Decisions](#detailed-integration-decisions)
  - [Process and SQL Commands Explanation](#process-and-sql-commands-explanation)
  - [Views Description and Data Retrieval](#views-description-and-data-retrieval)
  - [Queries on Views](#queries-on-views)
- [Backup Information](#backup-information)
- [Next Steps](#next-steps)

## Overview
This README documents Phase 3 of the university dormitory management system integration project, focusing on merging the new department's database with our existing system. David, the university manager, needed a unified database to manage managers, leases, and student rentals effectively. This phase involved importing foreign schemas, modifying tables, creating views, running queries, and ensuring data integrity with backups. All changes were carefully planned to support David's goal of streamlined operations.

## Files Included
- **DSD of the New Department**: `images/DSD_final.png`
- **ERD of the New Department**: `images/ERDother.png`
- **Combined ERD**: `images/ERD_COMBINDE.png`
- **DSD Post-Integration**: `images/DSDother.png`
- **Integrate.sql**: SQL script for table creation and modifications.
- **Views.sql**: SQL script for creating views and associated queries.
- **Backup3**: `Backups/Backup3__20_05_2025` (created on May 20, 2025).
- **Project Report Phase 3**: This README, detailing diagrams, decisions, processes, views, and queries.

## Integration Decisions and Rationale
We decided to define dorm managers as inheriting from employees, ensuring they inherit attributes like names from the `employee_local` table. This decision streamlined data management by reducing redundancy and ensuring consistency across HR and dormitory systems. Since managers are employees, their names and other details should be sourced from a single table (`employee_local`), avoiding duplicate data entry and potential inconsistencies. This inheritance approach also simplified joins in views and queries, making it easier for David to oversee manager-related operations.

## Summary of Changes
- **Removed Redundant Columns**: Dropped the `fullname` column from `dorm_management` since managers inherit names from `employee_local`.
- **Updated Data**: Modified manager emails in `dorm_management` to follow a standard university format based on employee names.
- **Corrected Data Mismatches**: Swapped `name` and `location` in `department_local` to fix an error in the received database.
- **Imported and Localized Tables**: Copied remote tables (e.g., `_remote`) to local tables (e.g., `_local`) to apply constraints.
- **Added Constraints**: Introduced primary keys, foreign keys, and NOT NULL constraints to ensure data integrity.
- **Added New Positions**: Inserted two new positions (`Unpaid Leave`, `Subject to Termination`) to resolve missing foreign key references.
- **Created Views and Queries**: Built views to integrate data and queries to support David's management needs.

**Rationale**: These changes aimed to create a unified, consistent database by eliminating redundancy, correcting errors, and enforcing data integrity. Importing and localizing tables allowed us to apply necessary constraints, while views and queries provided David with actionable insights into manager performance and lease management.

## Project Report Phase 3

### Screenshots of DSD and ERD Diagrams
- **DSD of the New Department**:  
  ![DSD Final](images/DSD_final.png)  
  Represents the structure of the new department’s database.

- **ERD of the New Department**:  
  ![ERD New Department](images/ERDother.png)  
  Shows the entity relationships in the new department’s database.

- **Combined ERD**:  
  ![Combined ERD](images/ERD_COMBINDE.png)  
  Illustrates the integrated database structure post-merger.

- **DSD Post-Integration**:  
  ![DSD Post-Integration](images/DSDother.png)  
  Displays the updated data structure after integration.

### Detailed Integration Decisions
- **Manager Inheritance from Employees**: Defined dorm managers as inheriting from employees, removing the `fullname` column from `dorm_management` to avoid redundancy.
- **Foreign Schema Import**: Imported remote tables using:  
  ```sql
  IMPORT FOREIGN SCHEMA public
  FROM SERVER otherdatabase_server
  INTO public;
  ```
- **Email Standardization**: Updated manager emails to a university format (`first.last@staff.university.ac.il`) based on `employee_local` names.
- **Data Correction**: Fixed a mismatch in `department_local` by swapping `name` and `location`.
- **Table Localization**: Copied remote tables to local ones (e.g., `employee_remote` to `employee_local`) to apply constraints.
- **Constraints**: Added primary keys (e.g., `pk_employee`), foreign keys (e.g., `fk_contract_employee`), and NOT NULL constraints to ensure data integrity.
- **New Positions**: Added `Unpaid Leave` (position_id 0) and `Subject to Termination` (position_id -1) to `position_local` to resolve foreign key issues.

### Process and SQL Commands Explanation
The integration process involved:
1. **Schema Import**: Imported foreign tables to access the new department’s data.
2. **Data Cleanup**: Removed redundant columns and corrected data mismatches.
3. **Table Localization**: Created local copies of remote tables for constraint application.
4. **Constraint Enforcement**: Added primary and foreign keys to maintain relationships.
5. **Testing**: Inserted test data (e.g., manager ID 450) to verify constraints.
6. **Views and Queries**: Created views to integrate data and queries to provide insights.

Key SQL scripts are available in:
- [Integrate.sql](Integrate.sql)
- [Views.sql](Views.sql)

### Views Description and Data Retrieval
#### View 1: ManagerEmployeeContractProfile
- **Description**: Integrates data from `employee_local`, `dorm_management`, and `contract_local` to provide a comprehensive profile of managers, including employee details, dorm management info, and contract details.  
  ![View 1 Diagram](images/VIEW1.png)
- **Data Retrieval**:  
  ```sql
  SELECT * FROM public.ManagerEmployeeContractProfile LIMIT 10;
  ```

#### View 2: RentalLeaseEmployeeContract
- **Description**: Connects rental and lease data from the dormitory system with employee contract details, focusing on managers overseeing student leases, including rental details, lease terms, and contract information.  
  ![View 2 Diagram](images/view2.png)
- **Data Retrieval**:  
  ```sql
  SELECT * FROM public.RentalLeaseEmployeeContract LIMIT 10;
  ```

### Queries on Views
#### Query 1 on ManagerEmployeeContractProfile
- **Description**: Returns managers with active contracts as of May 20, 2025, including their employee ID, name, position, department, hire date, and contract dates, sorted by name.
- **SQL**:  
  ```sql
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
  ```
- **Output**:  
  ![Query 1 on View 1 Output](images/qurey1onview1.png)

#### Query 2 on ManagerEmployeeContractProfile
- **Description**: Returns managers earning a salary above 15,000, including their employee ID, name, position, department, hire date, and salary, sorted by salary in descending order.
- **SQL**:  
  ```sql
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
  ```
- **Output**:  
  ![Query 2 on View 1 Output](images/qurey2onview1.png)

#### Query 1 on RentalLeaseEmployeeContract
- **Description**: Returns lease details for leases with discounts above 17% offered by managers not in Sales, Marketing, or Finance departments, including department ID, department name, lease ID, discount percentage, contract date, and position title, sorted by discount percentage in descending order.
- **SQL**:  
  ```sql
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
  ```
- **Output**:  
  ![Query 1 on View 2 Output](images/qurey1onview2.png)

#### Query 2 on RentalLeaseEmployeeContract
- **Description**: Returns managers who have signed at least 5 leases and earn a salary of 17,000 or less, including their manager ID, lease count, salary, and department name, sorted by lease count in descending order.
- **SQL**:  
  ```sql
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
  ```
- **Output**:  
  ![Query 2 on View 2 Output](images/qurey2onview2.png)

## Backup Information
- **Backup File**: `Backups/Backup3__20_05_2025`  
 ---