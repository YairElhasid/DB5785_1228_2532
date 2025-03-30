## Project Report: University Management System – Dormitory Management Unit

### Submitted By:
- **Yair Elhasid**
- **Elad Solomon**

---

## Table of Contents
1. [Introduction](#introduction)
2. [ERD and DSD Diagrams](#erd-and-dsd-diagrams)
3. [Design Decisions](#design-decisions)
4. [Data Insertion Methods](#data-insertion-methods)
   - [Method 1: Data Generation with Mockaroo](#method-1-mockaroo)
   - [Method 2: SQL INSERT Generation with Python](#method-2-sql-insert)
   - [Method 3: CSV Generation with Python](#method-3-csv)
5. [Backup and Restore](#backup-and-restore)

---

## Phase 1: Database Design and Construction

### Introduction
The University Management System is designed to manage all activities related to the university, including students, academic and administrative staff, buildings, maintenance, and more. The unit we chose to focus on is dormitory management, which includes registering students to dormitories, managing lease agreements, maintaining dormitory buildings, and managing the staff responsible for them.

The system's data includes student details, dormitory managers, residential buildings, apartments, rooms, lease agreements, active rentals, and maintenance requests. The main functionality enables tracking room assignments for students, managing lease agreements, and efficiently handling maintenance requests. The goal is to create a flexible system that supports the university's changing needs while maintaining data integrity and accuracy.

**Related Files:**
- [Create Tables Script](createTables.sql)
- [Drop Tables Script](dropTables.sql)
- [Select All Data Script](selectAll.sql)

---

## ERD and DSD Diagrams

### ERD Description
The ERD diagram describes the relationships between entities in the system:
- **Student**: Personal details (ID number, name, gender, date of birth, enrollment date, contact details, field of study).
- **Dormitory Management**: Manager details (ID number, full name, contact details, employment start date).
- **Building**: Dormitory building details (ID number, name, address, maximum number of apartments, responsible manager).
- **Apartment**: Apartment details within buildings (ID number, building number, room capacity, floor, maximum number of rooms).
- **Room**: Room details (ID number, maximum capacity of people, presence of a balcony, apartment and building number).
- **Lease Agreement**: Agreement management (ID number, contract date, discount percentage, manager who executed the agreement).
- **Rental**: Linking students to rooms (student number, room number, agreement number, check-in and check-out dates).
- **Maintenance Request**: Managing maintenance requests (ID number, description, request and resolution dates, priority, link to relevant entities if necessary).

![ERD Diagram](ERD.png)

### DSD Description
The DSD diagram details the structure of the tables, including columns, data types, and keys (primary and foreign), ensuring data consistency according to the ERD.

![DSD Diagram](DSD.png)

---

## Design Decisions

During the system design, several key design decisions were made:
1. **Students Without Dormitory Rentals**: We created 700 students – more than the requirement (400) to demonstrate that some students do not rent a dormitory apartment. Since there is a reality where students may live outside the dormitories, we defined the relationship between a student and a rental as optional.
2. **Flexibility in Maintenance Requests**: Maintenance requests are not required to be associated with a specific student, room, or lease agreement, to allow reporting of issues in common areas or unoccupied rooms.
4. **Building and Room Capacity Limits**: Each room includes a `MaxPeople` attribute, and rentals respect this limit, allowing multiple students per room but not illogical or illegal assignments. Similarly, restrictions and checks were set for the maximum number of rooms per apartment and the maximum number of apartments per building. These decisions aim to ensure flexibility, alignment with reality, and data integrity.
5. **Maintenance Requests as Needed**: There is no limit on the number of maintenance requests that can be opened, based on realistic considerations. Additionally, there is no obligation to open a maintenance request – only when there is a need.

---

## Data Insertion Methods

We implemented three methods for inserting data into the database, each supporting the creation of consistent data.

### Method 1: Data Generation with Mockaroo
The Mockaroo service was used to generate initial mock data for testing. It provided random data for the apartments table. Subsequently, the generated data was loaded into the database.

![Mockaroo Screenshot](mockarooFiles/mockaroo.png)  
![Import Data into Apartments Table](images/Import%20data%20from%20mockaroo%20csv%20file%20into%20apartments%20table.png)  
![Successful Import to Apartments Table](images/Successful%20import%20from%20mockaroo%20csv%20file%20to%20apartment%20table.png)  
[View `MOCK_DATA.csv`](mockarooFiles/MOCK_DATA.csv)

### Method 2: SQL INSERT Generation with Python
Using a Python script, we created `INSERT INTO` commands for all tables, which were written to `.sql` files. This method allows us full control over the relationships between the data. With Python, we can generate data that relies on relationships between tables and logical constraints we established during the database design. In implementing the Python script, we built functions to create mock data and also utilized a library for generating mock data in Python.

![Inserting Data into Student Table](images/Inserting%20data%20into%20a%20student%20table%20using%20SQL%20commands.png)  
![Student Table After Data Entry](images/Student%20table%20after%20data%20entry.png)  
[View `data_generator.py`](Programing/data_generator.py)  
[View `student.sql`](Programing/sql%20[insert]%20files/student.sql)  
[View `dorm_management.sql`](Programing/sql%20[insert]%20files/dorm_management.sql)  
[View `building.sql`](Programing/sql%20[insert]%20files/building.sql)  
[View `apartment.sql`](Programing/sql%20[insert]%20files/apartment.sql)  
[View `room.sql`](Programing/sql%20[insert]%20files/room.sql)  
[View `lease.sql`](Programing/sql%20[insert]%20files/lease.sql)  
[View `rental.sql`](Programing/sql%20[insert]%20files/rental.sql)  
[View `maintenance_request.sql`](Programing/sql%20[insert]%20files/maintenance_request.sql)  
[View Combined Insert Script](insertTables.sql)

### Method 3: CSV Generation with Python
The same Python script also created `.csv` files with data identical to that generated via SQL INSERT commands. This method allows importing data into the database and loading it into the tables.

![Import Data into Dorm Management Table](images/Import%20data%20into%20the%20dorm%20management%20table%20from%20an%20csv%20file.png)  
![Successful Import to Dorm Management Table](images/Successful%20import%20to%20dorm%20management%20table%20from%20scv%20file.png)  
[View `data_generator.py`](Programing/data_generator.py)  
[View `student.csv`](Programing/csv%20files/student.csv)  
[View `dorm_management.csv`](Programing/csv%20files/dorm_management.csv)  
[View `building.csv`](Programing/csv%20files/building.csv)  
[View `apartment.csv`](Programing/csv%20files/apartment.csv)  
[View `room.csv`](Programing/csv%20files/room.csv)  
[View `lease.csv`](Programing/csv%20files/lease.csv)  
[View `rental.csv`](Programing/csv%20files/rental.csv)  
[View `maintenance_request.csv`](Programing/csv%20files/maintenance_request.csv)

---

## Backup and Restore

### Backup Process
We performed a full backup of the database using pgAdmin. The backup includes the table structure and all data in the database.

![Creating Backup File](images/Creating%20the%20database%20backup%20file.png)  
![Backup Successfully Created](images/The%20database%20backup%20file%20was%20created%20successfully..png)  
[View Backup File](Backups/backup_28_03_2025)

### Restore Process
We restored the backup to a new database to verify data integrity. The process successfully restored all tables and the data we created within them.

![Restoring from Backup File](images/Restoring%20from%20the%20backup%20file.png)  
![Successful Restoration](images/Successful%20restoration%20from%20backup%20file.png)

---
