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
    vehicle_ID VARCHAR(10)
    
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
    payment_date TEXT,
    FOREIGN KEY(reservation_id) REFERENCES reservations(reservation_id)
);
'''
cursor.execute(create_users_table)
cursor.execute(create_cars_table)
cursor.execute(create_maintenance_table)
cursor.execute(create_reservations_table)
cursor.execute(create_payments_table)

create_trigger_set_in_maintenance = '''CREATE TRIGGER IF NOT EXISTS set_in_maintenance
AFTER INSERT ON maintenance
FOR EACH ROW
BEGIN
    UPDATE cars SET in_maintenance = 1 WHERE vehicle_ID = NEW.vehicle_ID;
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
BEGIN
    UPDATE cars SET reserved = 1 WHERE vehicle_ID = NEW.car_id;
END;'''

cursor.execute(create_trigger_set_in_maintenance)
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
    ),
    payment_date = DATE('now')
    WHERE amount IS NULL;
'''

sample_data_customers = [
    (1,"user1","John Doe","pass","Male"),
    (2,"user2","Jane Smith","pass","Female"),
]
cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?)", sample_data_customers)

sample_data_cars = [
    ("KA14CD2007", "TOYOTA", 2400),
    ("KA39BW2077", "Mahindra", 2000),
    ("KA14MX4500", "Honda", 1500),
    ("KA10AB1234", "Ford", 1800),
    ("KA25DF5678", "Hyundai", 1600),
    ("KA18GH9012", "Nissan", 2100),
    ("KA20JK3456", "Maruti", 1300),
    ("KA30LM7890", "BMW", 3500),
    ("KA22QR1122", "Audi", 4000),
    ("KA11ST3344", "Chevrolet", 1700)
]
cursor.executemany("INSERT INTO cars (vehicle_ID, brand, price_per_day) VALUES (?, ?, ?)", sample_data_cars)

sample_data_reservations = [
    (1, "KA14CD2007", "2024-11-01", "2024-11-05"),  
    (2, "KA39BW2077", "2024-11-03", "2024-11-07"),  
]
cursor.executemany("INSERT INTO reservations (customer_ID, car_id, start_date, end_date) VALUES (?, ?, ?, ?)", sample_data_reservations)

sample_data_maintenance = [
    ("KA14MX4500",)
]
cursor.executemany("INSERT INTO maintenance (vehicle_ID) VALUES (?)", sample_data_maintenance)

sample_data_payments = [
    (1,),  # Payment made for reservation 1
    (2,)   # Payment made for reservation 2
]
cursor.executemany("INSERT INTO payments (reservation_id, amount, payment_date) VALUES (?, NULL, NULL)", sample_data_payments)
cursor.execute(create_procedure) # call procedure

conn.commit()
conn.close()
