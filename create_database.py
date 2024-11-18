import sqlite3
conn = sqlite3.connect("rent_a_car.db")
cursor = conn.cursor()

create_users_table = '''
CREATE TABLE IF NOT EXISTS users (
    Customer_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    Name VARCHAR(25),
    password TEXT,
    Gender TEXT
);
'''
create_cars_table = '''
CREATE TABLE IF NOT EXISTS cars (
    vehicle_ID VARCHAR(10) PRIMARY KEY,
    brand TEXT NOT NULL,
    price_per_day REAL NOT NULL,
    in_maintenance INTEGER DEFAULT 0,
    reserved INTEGER DEFAULT 0
    CHECK (in_maintenance + reserved <= 1)
);
'''
create_maintenance_table = '''
CREATE TABLE IF NOT EXISTS maintenance (
    maintenance_schedule_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_ID VARCHAR(10),
    iterance INTEGER DEFAULT 0,
    FOREIGN KEY(vehicle_ID) REFERENCES cars(vehicle_ID)  
);
'''
create_reservations_table = '''
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_ID INTEGER,
    car_id TEXT,
    start_date TEXT,
    end_date TEXT,
    is_paid INTEGER DEFAULT 0,
    FOREIGN KEY(customer_ID) REFERENCES customers(customer_ID),
    FOREIGN KEY(car_id) REFERENCES cars(vehicle_ID)
);
'''
create_payments_table = '''
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id INTEGER,
    amount INTEGER,
    FOREIGN KEY(reservation_id) REFERENCES reservations(reservation_id)
);
'''
create_discount_table = '''
CREATE TABLE IF NOT EXISTS discounts (
    discount_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_ID INTEGER,
    discount_code INTEGER,
    FOREIGN KEY(customer_ID) REFERENCES customers(customer_ID)
);
'''

cursor.execute(create_users_table)
cursor.execute(create_cars_table)
cursor.execute(create_maintenance_table)
cursor.execute(create_reservations_table)
cursor.execute(create_payments_table)
cursor.execute(create_discount_table)

permissions='''
CREATE ROLE 'admin'
CREATE ROLE 'user'

GRANT ALTER, UPDATE, SELECT, DELETE ON cars TO 'admin'
GRANT ALTER, UPDATE, SELECT, DELETE ON maintenance TO 'admin'
GRANT ALTER, UPDATE, SELECT, DELETE ON reservations TO 'admin'
GRANT ALTER, UPDATE, SELECT, DELETE ON discounts TO 'admin'

GRANT INSERT ON users TO 'user'
GRANT INSERT ON reservations TO 'user'
GRANT INSERT ON payments TO 'user'
'''

create_trigger_set_maintenance = '''CREATE TRIGGER IF NOT EXISTS set_in_maintenance
AFTER INSERT ON maintenance
FOR EACH ROW
BEGIN
    UPDATE cars SET in_maintenance = 1 WHERE vehicle_ID = NEW.vehicle_ID;
END;'''

create_trigger_reset_maintenance = '''CREATE TRIGGER IF NOT EXISTS reset_in_maintenance
AFTER DELETE ON maintenance
FOR EACH ROW
BEGIN
    UPDATE cars SET in_maintenance = 0 WHERE vehicle_ID = OLD.vehicle_ID;
END;'''

create_trigger_SetIsPaidAfterPayment = '''CREATE TRIGGER IF NOT EXISTS SetIsPaidAfterPayment
AFTER UPDATE OF amount ON payments
FOR EACH ROW
WHEN NEW.amount IS NOT NULL
BEGIN
    UPDATE reservations
    SET is_paid = 1
    WHERE reservation_id = NEW.reservation_id;
END;'''

create_trigger_SetReservation = '''CREATE TRIGGER IF NOT EXISTS SetReservation
AFTER INSERT ON reservations
FOR EACH ROW
WHEN date('now') <  NEW.end_date
BEGIN
    UPDATE cars SET reserved = 1 WHERE vehicle_ID = NEW.car_id;
END;'''

cursor.execute(create_trigger_set_maintenance)
cursor.execute(create_trigger_reset_maintenance)
cursor.execute(create_trigger_SetIsPaidAfterPayment)
cursor.execute(create_trigger_SetReservation)

create_procedure ='''
    UPDATE payments
    SET amount = (
        SELECT 
            (julianday(r.end_date) - julianday(r.start_date)) * c.price_per_day
        FROM 
            reservations r
        JOIN 
            cars c ON r.car_id = c.vehicle_ID
        WHERE 
            r.reservation_id = payments.reservation_id
    )
    WHERE amount IS NULL;
'''



sample_data_customers = [
    (1,"user1","John Doe","pass1","Male"),
    (2,"user2","Jane Smith","pass2","Female"),
    (3,"user3","David Williams","pass3","Male"),
    (4,"user4","Emma Johnson","pass4","Female"),
    (5,"user5","Michael Brown","pass5","Male"),
    (6,"user6","Sarah Davis","pass6","Female"),
    (7,"user7","James Garcia","pass7","Male"),
    (8,"user8","Emily Martinez","pass8","Female"),
    (9,"user9","William Rodriguez","pass9","Male"),
    (10,"user10","Olivia Wilson","pass10","Female"),
    (11,"user11","Benjamin Lee","pass11","Male"),
    (12,"user12","Sophia Allen","pass12","Female"),
    (13,"user13","Lucas Young","pass13","Male"),
    (14,"user14","Mia King","pass14","Female"),
    (15,"user15","Ethan Scott","pass15","Male"),
    (16,"user16","Charlotte Green","pass16","Female"),
    (17,"user17","Henry Adams","pass17","Male"),
    (18,"user18","Amelia Baker","pass18","Female"),
    (19,"user19","Alexander Nelson","pass19","Male"),
    (20,"user20","Isabella Carter","pass20","Female"),
    (21,"user21","Daniel Mitchell","pass21","Male"),
    (22,"user22","Avery Perez","pass22","Female"),
    (23,"user23","Matthew Roberts","pass23","Male"),
    (24,"user24","Lily Walker","pass24","Female"),
    (25,"user25","Jack Hall","pass25","Male")
]
cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?)", sample_data_customers)

sample_data_cars = [
("KA14CD2007", "TOYOTA", 2400),("KA39BW2077", "Mahindra", 2000),("KA14MX4500", "Honda", 1500),("KA10AB1234", "Ford", 1800),
("KA25DF5678", "Hyundai", 1600),("KA18GH9012", "Nissan", 2100),("KA20JK3456", "Maruti", 1300),("KA30LM7890", "BMW", 3500),
("KA22QR1122", "Audi", 4000),("KA11ST3344", "Chevrolet", 1700),("KA14CD2008", "TOYOTA", 2400),("KA39BW2078", "Mahindra", 2000),
("KA14MX4501", "Honda", 1500),("KA10AB1235", "Maruti", 1300),("KA25DF5679", "Hyundai", 1600),("KA18GH9013", "Nissan", 2100),
("KA20JK3457", "Maruti", 1300),("KA30LM7891", "BMW", 3500),("KA22QR1123", "Audi", 4000),("KA11ST3345", "Honda", 1500),
("KA14CD2009", "Tesla", 5000),("KA39BW2079", "Ford", 2300),("KA14MX4502", "Chevrolet", 2100),("KA10AB1236", "Porsche", 6000),
("KA25DF5680", "Kia", 1900),("KA18GH9014", "Toyota", 2700),("KA20JK3458", "Mercedes", 4800),("KA22QR1124", "Land Rover", 5300),
]
cursor.executemany("INSERT INTO cars (vehicle_ID, brand, price_per_day) VALUES (?, ?, ?)", sample_data_cars)

sample_data_reservations = [
    (1, "KA14CD2007", "2024-12-01", "2024-12-05"),  
    (2, "KA39BW2077", "2024-12-03", "2024-12-07"),
    (2, "KA39BW2077", "2024-11-01", "2024-11-05"),
    (4, "KA14MX4500", "2024-10-11", "2024-10-19"),
    (3, "KA14CD2008", "2024-12-02", "2024-12-06"),
    (3, "KA25DF5679", "2024-12-10", "2024-12-15"),
    (6, "KA18GH9013", "2024-12-05", "2024-12-10"),
    (7, "KA20JK3457", "2024-12-01", "2024-12-04"),
    (8, "KA30LM7891", "2024-12-08", "2024-12-12"),
    (9, "KA22QR1123", "2024-12-10", "2024-12-14"),
    (3, "KA11ST3345", "2024-12-03", "2024-12-07"),
    (11, "KA20JK3456", "2024-10-20", "2024-10-25"),
    (12, "KA39BW2079", "2024-10-18", "2024-10-22"),
    (13, "KA14MX4502", "2024-10-15", "2024-10-19"),
    (3, "KA10AB1236", "2024-10-25", "2024-10-29"),
    (11, "KA25DF5680", "2024-12-01", "2024-12-05"),
    (16, "KA18GH9014", "2024-10-10", "2024-10-14"),
    (17, "KA20JK3458", "2024-10-07", "2024-10-11"),
    (3, "KA20JK3457", "2024-10-13", "2024-10-17"),
    (19, "KA22QR1124", "2024-12-02", "2024-12-06"),
    (20, "KA10AB1235", "2024-12-12", "2024-12-16"),
    (20, "KA14CD2007", "2024-10-12", "2024-10-16"),
    (11, "KA39BW2078", "2024-10-03", "2024-10-07"),
    (23, "KA14MX4501", "2024-12-07", "2024-12-11"),
    (25, "KA25DF5678", "2024-12-05", "2024-12-09"),
    (25, "KA18GH9012", "2024-12-09", "2024-12-13")  
]
cursor.executemany("INSERT INTO reservations (customer_ID, car_id, start_date, end_date) VALUES (?, ?, ?, ?)", sample_data_reservations)

sample_data_maintenance = [
    ("KA14MX4500",),("KA11ST3344",),("KA20JK3456",),("KA39BW2079",),("KA18GH9014",)
]
cursor.executemany("INSERT INTO maintenance (vehicle_ID) VALUES (?)", sample_data_maintenance)

sample_data_payments = [
    (1,),(2,),(9,),(10,),(11,),(20,),(21,)  
]
cursor.executemany("INSERT INTO payments (reservation_id, amount) VALUES (?, NULL)", sample_data_payments)
cursor.execute(create_procedure) # call procedure

conn.commit()
conn.close()
