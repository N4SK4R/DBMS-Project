import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
import matplotlib.pyplot as plt
import sqlite3

def show_top_3():

    cursor = conn.cursor()
        
    nested_query = '''
    SELECT u.Customer_ID, u.Name, SUM(
        (JULIANDAY(r.end_date) - JULIANDAY(r.start_date)) * c.price_per_day
    ) AS unpaid_total
    FROM users u
    JOIN reservations r ON u.Customer_ID = r.customer_ID
    JOIN cars c ON r.car_id = c.vehicle_ID
    WHERE r.is_paid = 0 AND DATE('now') < r.end_date
    AND u.Customer_ID IN (
    SELECT users.Customer_ID
    FROM users
    JOIN reservations ON users.Customer_ID = reservations.customer_ID
    JOIN cars ON reservations.car_id = cars.vehicle_ID
    WHERE reservations.is_paid = 1 OR DATE('now') > reservations.end_date
    GROUP BY users.Customer_ID
    ORDER BY SUM(
        (JULIANDAY(reservations.end_date) - JULIANDAY(reservations.start_date)) * cars.price_per_day
    ) DESC
    )
    GROUP BY u.Customer_ID
    ORDER BY unpaid_total DESC
    '''
    
    cursor.execute(nested_query)
    rows = cursor.fetchall()

    if rows:
        for row in rows:
            customer_id, name, unpaid_total = row
            discount_code = 20 
            cursor.execute('''
                INSERT INTO discounts (customer_ID, discount_code)
                VALUES (?, ?)
            ''', (customer_id, discount_code))
            print(f"Discount applied for customer ID: {customer_id}, Name: {name}, Discount Code: {discount_code}")
    else:
        print("No eligible customers found for discount.")

    conn.commit()
    
    top = tk.Toplevel(main_window)
    top.title("Discount For Users")
    top.geometry("600x400")

    tree = ttk.Treeview(top, columns=("Customer ID", "Name", "Total Amount Due"), show="headings")
    tree.heading("Customer ID", text="Customer ID")
    tree.heading("Name", text="Name")
    tree.heading("Total Amount Due", text="Total Amount Due (₹)")

    for row in rows:
        row = (row[0], row[1], f"{row[2]}")
        tree.insert("", "end", values=row)

    tree.pack(fill=tk.BOTH, expand=True)

def show_users_with_highest_paid():
    
    cursor = conn.cursor()
    
    procedure = '''
    SELECT users.Customer_ID, users.Name, SUM(
        (JULIANDAY(reservations.end_date) - JULIANDAY(reservations.start_date)) * cars.price_per_day
    ) AS total
    FROM users
    JOIN reservations ON users.Customer_ID = reservations.customer_ID
    JOIN cars ON reservations.car_id = cars.vehicle_ID
    WHERE reservations.is_paid = 1 OR date('now') > reservations.end_date 
    GROUP BY users.Customer_ID
    ORDER BY total DESC;
    '''    
    
    cursor.execute(procedure)
    rows = cursor.fetchall()

    top = tk.Toplevel(main_window)
    top.title("Users with Highest Paid Amount")
    top.geometry("800x400")

    tree = ttk.Treeview(top, columns=("Customer ID", "Name", "Total Amount Paid"), show="headings")
    tree.heading("Customer ID", text="Customer ID")
    tree.heading("Name", text="Name")
    tree.heading("Total Amount Paid", text="Total Amount Paid (₹)")

    for row in rows:
        row = (row[0], row[1], f"{row[2]}")
        tree.insert("", "end", values=row)

    tree.pack(fill=tk.BOTH, expand=True)
    button = tk.Button(top, text="Assign Discount", command=lambda: show_top_3())
    button.pack(padx=250)

def show_most_reserved_cars():

    cursor = conn.cursor()
    
    procedure = '''
    SELECT cars.vehicle_ID, cars.brand, cars.price_per_day, COUNT(reservations.car_id) AS reservation_count
    FROM cars
    LEFT JOIN reservations ON cars.vehicle_ID = reservations.car_id
    GROUP BY cars.brand
    ORDER BY reservation_count DESC;
    '''
    cursor.execute(procedure)
    rows = cursor.fetchall()

    brands = [row[1] for row in rows]
    reservation_counts = [row[3] for row in rows]

    # Generate the bar chart
    plt.figure(figsize=(10, 6))
    plt.barh(brands, reservation_counts, color='skyblue')
    plt.xlabel('Number of Reservations')
    plt.ylabel('Car Brand')
    plt.title('Most Reserved Car Brands')
    plt.gca().invert_yaxis()  # Invert y-axis to display highest counts at the top
    plt.tight_layout()
    plt.show()
    
    top = tk.Toplevel(main_window)
    top.title("Most Reserved Cars")
    top.geometry("800x400")

    columns=("Vehicle ID", "Brand", "Price per Day", "Reservation Count")
    table = ttk.Treeview(top, columns=columns, show="headings")
    
    for col in columns:
        table.heading(col, text=col)
        
    for row in rows:
        table.insert("", "end", values=row)

    table.pack(fill=tk.BOTH, expand=True)

# Function to toggle status in maintenance table
def open_edit_window(selected_row):
    car_id, brand, price = selected_row
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO maintenance (vehicle_ID) VALUES (?)", (car_id,))
        conn.commit()
        vehicle_window.destroy()
        show_vehicles()
    except sqlite3.Error:
        messagebox.showerror("Error", "Vehicle Booked for Reservation")

def delete_record(selected_row):
    id, car_id ,iter = selected_row
    cursor = conn.cursor()
    cursor.execute("DELETE FROM maintenance WHERE maintenance_schedule_ID = ?", (id,))
    conn.commit()

def show_maintenance():
    global vehicle_window
    vehicle_window = tk.Toplevel(main_window)
    vehicle_window.title("Maintenance")
    vehicle_window.geometry("600x300")

    table_frame = tk.Frame(vehicle_window)
    table_frame.pack(fill=tk.BOTH, expand=True)

    delete = tk.Button(vehicle_window, text="Delete Record", command=lambda: delete_record(table.item(table.focus())["values"]))
    delete.pack(side="left",padx=250)
    
    columns = ("maintenance_schedule_ID", "vehicle_ID", "Iterance")
    table = ttk.Treeview(table_frame, columns=columns, show="headings")
    table.pack(fill=tk.BOTH, expand=True)
    
    for col in columns:
        table.heading(col, text=col)

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM maintenance")
    rows = cursor.fetchall()

    for row in rows:
        table.insert("", "end", values=row)

def show_vehicles():
    global vehicle_window
    vehicle_window = tk.Toplevel(main_window)
    vehicle_window.title("Available Vehicles")
    vehicle_window.geometry("600x650")

    table_frame = tk.Frame(vehicle_window)
    table_frame.pack(fill=tk.BOTH, expand=True)

    edit_button = tk.Button(vehicle_window, text="Edit Status", command=lambda: open_edit_window(table.item(table.focus())["values"]))
    edit_button.pack(side="left",padx=250)
    
    columns = ("vehicle_ID", "brand", "price_per_day")
    table = ttk.Treeview(table_frame, columns=columns, show="headings")
    table.pack(fill=tk.BOTH, expand=True)

    for col in columns:
        table.heading(col, text=col)

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cars")
    rows = cursor.fetchall()

    for row in rows:
        car_id, brand, price_per_day, in_maintenance, reserved = row
        tag = "red" if in_maintenance == 1 else ""
        table.insert("", "end", values=(car_id, brand, price_per_day), tags=(tag,))

    table.tag_configure("red", background="red")

def show_reservations():
    reservation_window = tk.Toplevel(main_window)
    reservation_window.title("Reservations")
    reservation_window.geometry("1000x400")
    
    table_frame = tk.Frame(reservation_window)
    table_frame.pack(fill=tk.BOTH, expand=True)

    columns = ("reservation_ID", "customer", "vehicle_ID", "reservation_date", "return_date", "Total")
    table = ttk.Treeview(table_frame, columns=columns, show="headings")
    table.pack(fill=tk.BOTH, expand=True)

    for col in columns:
        table.heading(col, text=col)

    current_date = datetime.now().date()
    cursor = conn.cursor()
    cursor.execute('''SELECT r.reservation_id,c.Name ,r.car_id, r.start_date, r.end_date, r.is_paid, (JULIANDAY(r.end_date) - JULIANDAY(r.start_date)) * cars.price_per_day AS total_price
    FROM reservations r JOIN users c ON r.customer_ID = c.customer_ID JOIN cars on r.car_id = cars.vehicle_ID''')
    rows = cursor.fetchall()

    for row in rows:
        res_id, name, car_id, start, end, is_paid ,amt= row
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
        tag = "green" if is_paid == 1 else ""
        if current_date > end_date:
            tag = "blue" 
        table.insert("", "end", values=(res_id, name, car_id, start, end , amt), tags=(tag,))

    table.tag_configure("green", background="light green")
    table.tag_configure("blue", background="light blue")
    
    legend_frame = tk.Frame(reservation_window)
    legend_frame.pack(fill=tk.X, pady=5)

    green_label = tk.Label(legend_frame, text="Paid", bg="light green", font=("Arial", 10))
    green_label.pack(side=tk.LEFT, padx=10)

    blue_label = tk.Label(legend_frame, text="Completed", bg="light blue", font=("Arial", 10))
    blue_label.pack(side=tk.LEFT, padx=10)

def show_payments():
    payment_window = tk.Toplevel(main_window)
    payment_window.title("Payments")
    payment_window.geometry("600x300")

    table_frame = tk.Frame(payment_window)
    table_frame.pack(fill=tk.BOTH, expand=True)

    columns = ("payment_ID","reservation_ID", "amount", "payment_date")
    table = ttk.Treeview(table_frame, columns=columns, show="headings")
    table.pack(fill=tk.BOTH, expand=True)

    for col in columns:
        table.heading(col, text=col)

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM payments")
    rows = cursor.fetchall()

    for row in rows:
        table.insert("", "end", values=row)

# Function to open the main "RENT-A-CAR" page
def admin_dashboard():
    global main_window, conn
    conn = sqlite3.connect("rent_a_car.db")
    
    main_window = tk.Tk()
    main_window.title("RENT-A-CAR")
    main_window.geometry("1200x650")

    style = ttk.Style()
    style.theme_use("clam")

    style.map("Treeview",
    background=[("selected", "white")], 
    foreground=[("selected", "black")]) 
     
    header_frame = tk.Frame(main_window)
    header_frame.pack(pady=10)

    title_label = tk.Label(header_frame, text="RENT-A-CAR", font=("Arial", 20))
    title_label.pack(side="left", padx=10)

    btn_show_reserved_cars = tk.Button(header_frame, text="Report 1", command=show_most_reserved_cars)
    btn_show_reserved_cars.pack(side="left", padx=15)
    
    btn_show_due = tk.Button(header_frame, text="Report 2", command=show_users_with_highest_paid)
    btn_show_due.pack(side="left", padx=10)
    
    button_frame = tk.Frame(main_window)
    button_frame.pack(side=tk.LEFT, padx=20, pady=20)

    # Buttons to open each table
    button_texts = ["Reservations", "Vehicles", "Maintenance", "Payments"]
    button_functions = [show_reservations, show_vehicles, show_maintenance, show_payments]

    for text, command in zip(button_texts, button_functions):
        button = tk.Button(button_frame, text=text, width=15, height=2, command=command)
        button.pack(pady=5)

    table_frame = tk.Frame(main_window, borderwidth=1, relief="solid")
    table_frame.pack(side=tk.RIGHT, padx=20, pady=20, fill=tk.BOTH, expand=True)

    columns = ("customer_ID","Username","Name", "Gender")
    table = ttk.Treeview(table_frame, columns=columns, show="headings")
    table.pack(fill=tk.BOTH, expand=True)

    for col in columns:
        table.heading(col, text=col)

    def fetch_data():
        cursor = conn.cursor()
        cursor.execute("SELECT Customer_ID, username, Name, Gender FROM users")
        rows = cursor.fetchall()
        return rows

    def display_data():
        for row in table.get_children():
            table.delete(row)
        rows = fetch_data()
        for row in rows:
            table.insert("", "end", values=row)

    display_data()

    main_window.mainloop()
