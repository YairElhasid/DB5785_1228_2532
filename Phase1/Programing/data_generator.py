import csv
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker with Hebrew locale
fake = Faker('he_IL')

# Existing name lists (unchanged)
male_first_names = [
    "David", "Eitan", "Yossi", "Daniel", "Yonatan", "Nadav", "Aviv", "Lior", "Gal", "Itai",
    "Yaakov", "Omer", "Shay", "Gadi", "Alon", "Ron", "Omri", "Gavriel", "Asaf", "Benny"
]
female_first_names = [
    "Noa", "Amit", "Yael", "Tamar", "Shira", "Rivka", "Maya", "Eden", "Michal", "Talia",
    "Hadar", "Tal", "Yarden", "Reut", "Iris", "Shaked", "Raz", "Nitzan", "Eliana", "Hila"
]
last_names = [
    "Levi", "Cohen", "Mizrahi", "Peretz", "Biton", "Avraham", "Shimon", "Malka", "Eliyahu", "Amar",
    "Gabbay", "Halevi", "Dahan", "Shushan", "Azoulay", "Zamir", "Hadad", "Tal", "Shohat",
    "Katz", "Shapiro", "Ben-David", "Friedman", "Hershkovitz", "Elbaz", "Dayan", "Gerstein",
    "Harari", "Turgeman", "Alfasi", "Halperin", "Shabtai", "Ben-Tovim", "Navon", "Sharabi", "Rabinovich", "Menachem",
    "Shoshani", "Ozeri", "Ben-Ami", "Ben-Zvi", "Sasson", "Tzadok", "Luzon", "Gavish", "Yaron", "Goren", "Kadosh",
    'Cohen', 'Levi', 'Mizrahi', 'Peretz', 'Ben-David', 'Sharon', 'Rosenberg', 'Berkovitz',
    'Goldstein', 'Baruch', 'Shalom', 'Kalach', 'Shapira', 'Abraham', 'Lavi', 'Zohar',
    'Shaked', 'Golan', 'Katz', 'Carmi', 'Ezra', 'Tzukrel', 'Ashkenazi', 'Chaimovitz',
    'Bashan', 'Amar', 'Gabbai', 'Elbaz', 'Safra', 'Zarfati', 'Shalmon', 'Soffer',
    'Avrahami', 'Kuperstein', 'Wexler', 'Harel', 'Shoshan', 'Gavrieli', 'Natan',
    'Sasson', 'Givon', 'Perlman', 'Harari', 'Shuster', 'Kadosh', 'Mor', 'Golan', 'Tzukrel'
]
first_names = [
    'Amit', 'Noa', 'Yair', 'Shira', 'Oren', 'Maya', 'Tomer', 'Yaara', 'Itamar', 'Moran',
    'Lior', 'Noya', 'Shani', 'Yuval', 'Zohar', 'Dana', 'Erez', 'Avigail', 'Liad', 'Talia',
    'Oded', 'Michal', 'Gal', 'Hila', 'Yuval', 'Netta', 'Ben', 'Yael', 'Doron', 'Moran',
    'Nadav', 'Inbal', 'Kfir', 'Meir', 'Adi', 'Dvir', 'Batya', 'Amir', 'Reut', 'Kfir',
    'Roni', 'Tzachi', 'Zvika', 'Alon', 'Hadar', 'Miki', 'Eli', 'Roni', 'Nir'
]

def fake_israeli_name():
    gender = random.choice(['Male', 'Female'])
    first_name = random.choice(male_first_names if gender == 'Male' else female_first_names)
    last_name = random.choice(last_names)
    return f"{first_name} {last_name} {gender}"

def fake_israeli_full_name():
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    return f"{first_name} {last_name}"

# Existing lists (unchanged)
majors = ['Computer Science', 'Mathematics', 'Physics', 'Biology', 'Chemistry']
streets = [
    "Dizengoff", "Rothschild", "Allenby", "Ben Yehuda", "Herzl", "Jabotinsky",
    "King George", "Ibn Gabirol", "Begin", "Kaplan", "HaYarkon", "Eilat",
    "Yehuda Halevi", "HaPalmach", "Emek Refaim", "Jaffa", "Shlomtzion HaMalka",
    "Agron", "Derech Hevron", "Ben Gurion", "Moriah", "Hertzel", "Yigal Alon",
    "Weizmann", "HaMasger", "Arlozorov", "Sokolov", "Henrietta Szold",
    "Rager Boulevard", "Yitzhak Rambo"
]
building_names = [
    "Herzl Residence", "Weizmann Hall", "Ben Gurion Towers", "Rabin House", "Golda Residence",
    "Einstein Lodge", "Technion Heights", "Negev Hall", "Jerusalem Heights", "Galilee Residence",
    "The Arava Tower", "Shamir Hall", "Peres House", "Carmel Residence", "Shaked Hall"
]
cities = ['Jerusalem', 'Tel Aviv', 'Haifa', 'Beersheba']
issues = [
    "Leaky faucet", "Broken window", "Elevator issue", "AC not working", "Clogged drain",
    "No hot water", "Flickering lights", "Power outage", "Door lock malfunction",
    "Water leak from ceiling", "Toilet not flushing", "Heating system failure",
    "Broken refrigerator", "Gas leak", "Internet connectivity issues", "Mold on walls",
    "Broken intercom", "Cracked floor tiles", "Pest infestation", "Washing machine not working",
    "Dryer not heating", "Broken showerhead", "Peeling paint", "Damaged furniture",
    "Smoke detector not working", "Loose electrical outlet", "Noisy plumbing",
    "Ventilation problems", "Flooded basement", "Roof leakage"
]
priorities = ['Low', 'Medium', 'High']

# Dictionaries to store relationships
students = {}
managers = {}
buildings = {}
apartments = {}
rooms = {}
leases = {}
rentals = {}

# Helper function to format values for SQL
def sql_format(value):
    if value == '' or value is None:
        return 'NULL'
    elif isinstance(value, bool):
        return '1' if value else '0'
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, (datetime, timedelta)):
        return f"'{value.strftime('%Y-%m-%d')}'"
    else:
        return f"'{value}'"

# 1. Generate student.csv and student.sql (unchanged)
with open('student.csv', 'w', newline='', encoding='utf-8') as f_csv, \
        open('student.sql', 'w', encoding='utf-8') as f_sql:
    writer = csv.writer(f_csv)
    writer.writerow(['StudentID', 'FirstName', 'LastName', 'Gender', 'DateOfBirth', 'EnrollmentDate', 'PhoneNumber', 'Email', 'Major'])
    for student_id in range(1, 701):
        first_name, last_name, gender = fake_israeli_name().split()
        date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=25)
        enrollment_date = fake.date_between(start_date='-2y', end_date='today')
        phone_number = f"+972 5{random.randint(0, 9)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        email = f"{first_name.lower()}.{last_name.lower()}@university.ac.il"
        major = random.choice(majors)
        writer.writerow([student_id, first_name, last_name, gender, date_of_birth, enrollment_date, phone_number, email, major])
        f_sql.write(f"INSERT INTO student VALUES ({student_id}, '{first_name}', '{last_name}', '{gender}', '{date_of_birth}', '{enrollment_date}', '{phone_number}', '{email}', '{major}');\n")
        students[student_id] = (first_name, last_name, gender, date_of_birth, enrollment_date, phone_number, email, major)

# 2. Generate dorm_management.csv and dorm_management.sql (unchanged)
with open('dorm_management.csv', 'w', newline='', encoding='utf-8') as f_csv, \
        open('dorm_management.sql', 'w', encoding='utf-8') as f_sql:
    writer = csv.writer(f_csv)
    writer.writerow(['ManagerID', 'FullName', 'PhoneNumber', 'Email', 'HireDate'])
    for manager_id in range(1, 401):
        full_name = fake_israeli_full_name()
        phone_number = f"+972 5{random.randint(0, 9)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        email = f"{full_name.replace(' ', '.').lower()}@staff.university.ac.il"
        hire_date = fake.date_between(start_date='-10y', end_date='-1y')
        writer.writerow([manager_id, full_name, phone_number, email, hire_date])
        f_sql.write(f"INSERT INTO dorm_management VALUES ({manager_id}, '{full_name}', '{phone_number}', '{email}', '{hire_date}');\n")
        managers[manager_id] = (full_name, phone_number, email, hire_date)

# 3. Generate building.csv and building.sql
building_apartment_counts = {}
with open('building.csv', 'w', newline='', encoding='utf-8') as f_csv, \
        open('building.sql', 'w', encoding='utf-8') as f_sql:
    writer = csv.writer(f_csv)
    writer.writerow(['BuildingID', 'BuildingName', 'Address', 'MaxApartments', 'ManagerID'])
    for building_id in range(1, 401):
        building_name = random.choice(building_names)
        street = random.choice(streets)
        house_number = random.randint(1, 98)
        address = f"{street} {house_number}, {random.choice(cities)}"
        max_apartments = random.randint(2, 5)  # Each building can have 2-5 apartments
        manager_id = random.randint(1, 400)
        writer.writerow([building_id, building_name, address, max_apartments, manager_id])
        f_sql.write(f"INSERT INTO building VALUES ({building_id}, '{building_name}', '{address}', {max_apartments}, {manager_id});\n")
        buildings[building_id] = (building_name, address, max_apartments, manager_id)
        building_apartment_counts[building_id] = 0

# 4. Generate apartment.csv and apartment.sql
with open('apartment.csv', 'w', newline='', encoding='utf-8') as f_csv, \
        open('apartment.sql', 'w', encoding='utf-8') as f_sql:
    writer = csv.writer(f_csv)
    writer.writerow(['ApartmentID', 'BuildingID', 'RoomCapacity', 'FloorNumber', 'MaxRooms'])
    apartment_id = 1
    building_ids = list(range(1, 401))
    random.shuffle(building_ids)
    for building_id in building_ids:
        max_apartments = buildings[building_id][2]
        num_apartments = random.randint(1, max_apartments)  # At least 1, up to max
        for _ in range(num_apartments):
            if apartment_id > 400:
                break
            room_capacity = random.randint(3, 6)
            floor_number = random.randint(1, 10)
            max_rooms = random.randint(2, 4)  # Each apartment can have 2-4 rooms
            writer.writerow([apartment_id, building_id, room_capacity, floor_number, max_rooms])
            f_sql.write(f"INSERT INTO apartment VALUES ({apartment_id}, {building_id}, {room_capacity}, {floor_number}, {max_rooms});\n")
            apartments[apartment_id] = (building_id, room_capacity, floor_number, max_rooms)
            building_apartment_counts[building_id] += 1
            apartment_id += 1
    # Fill remaining apartments if less than 400
    while apartment_id <= 400:
        building_id = random.choice([b for b, count in building_apartment_counts.items() if count < buildings[b][2]])
        room_capacity = random.randint(3, 6)
        floor_number = random.randint(1, 10)
        max_rooms = random.randint(2, 4)
        writer.writerow([apartment_id, building_id, room_capacity, floor_number, max_rooms])
        f_sql.write(f"INSERT INTO apartment VALUES ({apartment_id}, {building_id}, {room_capacity}, {floor_number}, {max_rooms});\n")
        apartments[apartment_id] = (building_id, room_capacity, floor_number, max_rooms)
        building_apartment_counts[building_id] += 1
        apartment_id += 1

# 5. Generate room.csv and room.sql
apartment_room_counts = {apt_id: 0 for apt_id in apartments}
with open('room.csv', 'w', newline='', encoding='utf-8') as f_csv, \
        open('room.sql', 'w', encoding='utf-8') as f_sql:
    writer = csv.writer(f_csv)
    writer.writerow(['RoomID', 'MaxPeople', 'HasBalcony', 'ApartmentID', 'BuildingID'])
    room_id = 1
    apartment_ids = list(apartments.keys())
    random.shuffle(apartment_ids)
    for apartment_id in apartment_ids:
        building_id, _, _, max_rooms = apartments[apartment_id]
        num_rooms = random.randint(1, max_rooms)  # At least 1, up to max
        for _ in range(num_rooms):
            if room_id > 400:
                break
            max_people = random.randint(1, 3)  # Each room can have 1-3 people
            has_balcony = random.choice(["TRUE", "FALSE"])
            writer.writerow([room_id, max_people, has_balcony, apartment_id, building_id])
            f_sql.write(f"INSERT INTO room VALUES ({room_id}, {max_people}, {has_balcony}, {apartment_id}, {building_id});\n")
            rooms[room_id] = (max_people, has_balcony, apartment_id, building_id)
            apartment_room_counts[apartment_id] += 1
            room_id += 1
    # Fill remaining rooms if less than 400
    while room_id <= 400:
        apartment_id = random.choice([a for a, count in apartment_room_counts.items() if count < apartments[a][3]])
        building_id = apartments[apartment_id][0]
        max_people = random.randint(1, 3)
        has_balcony = random.choice([True, False])
        writer.writerow([room_id, max_people, has_balcony, apartment_id, building_id])
        f_sql.write(f"INSERT INTO room VALUES ({room_id}, {max_people}, {has_balcony}, {apartment_id}, {building_id});\n")
        rooms[room_id] = (max_people, has_balcony, apartment_id, building_id)
        apartment_room_counts[apartment_id] += 1
        room_id += 1

# 6. Generate lease.csv and lease.sql (unchanged)
with open('lease.csv', 'w', newline='', encoding='utf-8') as f_csv, \
        open('lease.sql', 'w', encoding='utf-8') as f_sql:
    writer = csv.writer(f_csv)
    writer.writerow(['LeaseID', 'ContractDate', 'DiscountPercent', 'ManagerID'])
    for lease_id in range(1, 401):
        contract_date = fake.date_between(start_date='-2y', end_date='-6m')
        discount_percent = round(random.uniform(0, 20), 2)
        manager_id = random.randint(1, 400)
        writer.writerow([lease_id, contract_date, discount_percent, manager_id])
        f_sql.write(f"INSERT INTO lease VALUES ({lease_id}, '{contract_date}', {discount_percent}, {manager_id});\n")
        leases[lease_id] = (contract_date, discount_percent, manager_id)

# 7. Generate rental.csv and rental.sql
room_occupancy = {room_id: 0 for room_id in rooms}
with open('rental.csv', 'w', newline='', encoding='utf-8') as f_csv, \
        open('rental.sql', 'w', encoding='utf-8') as f_sql:
    writer = csv.writer(f_csv)
    writer.writerow(['StudentID', 'RoomID', 'LeaseID', 'CheckInDate', 'CheckOutDate'])
    rental_count = 0
    student_ids = list(range(1, 401))
    random.shuffle(student_ids)
    for student_id in student_ids:
        available_rooms = [r for r, (max_p, _, _, _) in rooms.items() if room_occupancy[r] < max_p]
        if not available_rooms:
            continue
        room_id = random.choice(available_rooms)
        lease_id = random.randint(1, 400)
        check_in_date = fake.date_between(start_date='-3m', end_date='today')
        check_out_date = check_in_date + timedelta(days=random.randint(90, 365))
        writer.writerow([student_id, room_id, lease_id, check_in_date, check_out_date])
        f_sql.write(f"INSERT INTO rental VALUES ({student_id}, {room_id}, {lease_id}, '{check_in_date}', '{check_out_date}');\n")
        rentals[(student_id, room_id, lease_id)] = (check_in_date, check_out_date)
        room_occupancy[room_id] += 1
        rental_count += 1
        if rental_count >= 400:
            break
    # Fill remaining rentals if less than 400
    while rental_count < 400:
        student_id = random.randint(1, 400)
        available_rooms = [r for r, (max_p, _, _, _) in rooms.items() if room_occupancy[r] < max_p]
        if not available_rooms:
            break
        room_id = random.choice(available_rooms)
        lease_id = random.randint(1, 400)
        check_in_date = fake.date_between(start_date='-3m', end_date='today')
        check_out_date = check_in_date + timedelta(days=random.randint(90, 365))
        writer.writerow([student_id, room_id, lease_id, check_in_date, check_out_date])
        f_sql.write(f"INSERT INTO rental VALUES ({student_id}, {room_id}, {lease_id}, '{check_in_date}', '{check_out_date}');\n")
        rentals[(student_id, room_id, lease_id)] = (check_in_date, check_out_date)
        room_occupancy[room_id] += 1
        rental_count += 1

# 8. Generate maintenance_request.csv and maintenance_request.sql (unchanged)
with open('maintenance_request.csv', 'w', newline='', encoding='utf-8') as f_csv, \
        open('maintenance_request.sql', 'w', encoding='utf-8') as f_sql:
    writer = csv.writer(f_csv)
    writer.writerow(['RequestID', 'IssueDescription', 'RequestDate', 'ResolvedDate', 'Priority', 'ManagerID', 'StudentID', 'RoomID', 'LeaseID'])
    for request_id in range(1, 401):
        issue_description = random.choice(issues)
        request_date = fake.date_between(start_date='-3m', end_date='today')
        resolved_date = fake.date_between_dates(request_date, datetime.now().date()) if random.random() > 0.3 else ''
        priority = random.choice(priorities)
        manager_id = random.randint(1, 400)
        if random.random() > 0.2 and rentals:
            rental_key = random.choice(list(rentals.keys()))
            student_id, room_id, lease_id = rental_key
        else:
            student_id = room_id = lease_id = ''
        writer.writerow([request_id, issue_description, request_date, resolved_date, priority, manager_id, student_id, room_id, lease_id])
        resolved_date_sql = f"'{resolved_date}'" if resolved_date else 'NULL'
        student_id_sql = student_id if student_id else 'NULL'
        room_id_sql = room_id if room_id else 'NULL'
        lease_id_sql = lease_id if lease_id else 'NULL'
        f_sql.write(f"INSERT INTO maintenance_request VALUES ({request_id}, '{issue_description}', '{request_date}', {resolved_date_sql}, '{priority}', {manager_id}, {student_id_sql}, {room_id_sql}, {lease_id_sql});\n")

print("CSV and SQL files generated successfully with realistic building-apartment-room-student relationships!")