import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3

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

def show_maintenance():
    global vehicle_window
    vehicle_window = tk.Toplevel(main_window)
    vehicle_window.title("Maintenance")
    vehicle_window.geometry("600x300")

    table_frame = tk.Frame(vehicle_window)
    table_frame.pack(fill=tk.BOTH, expand=True)

    columns = ("maintenance_schedule_ID", "vehicle_ID", "status")
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
    vehicle_window.geometry("600x300")

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
    reservation_window.geometry("600x300")

    table_frame = tk.Frame(reservation_window)
    table_frame.pack(fill=tk.BOTH, expand=True)

    columns = ("reservation_ID", "customer", "vehicle_ID", "reservation_date", "return_date")
    table = ttk.Treeview(table_frame, columns=columns, show="headings")
    table.pack(fill=tk.BOTH, expand=True)

    for col in columns:
        table.heading(col, text=col)

    cursor = conn.cursor()
    cursor.execute('''SELECT r.reservation_id,c.Name ,r.car_id, r.start_date, r.end_date, r.is_paid
    FROM reservations r JOIN users c ON r.customer_ID = c.customer_ID''')
    rows = cursor.fetchall()

    for row in rows:
        res_id, name, car_id, start, end, is_paid = row
        tag = "green" if is_paid == 1 else ""
        table.insert("", "end", values=(res_id, name, car_id, start, end , is_paid), tags=(tag,))

    table.tag_configure("green", background="light green")

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
    main_window.geometry("600x400")

    title_label = tk.Label(main_window, text="RENT-A-CAR", font=("Arial", 20))
    title_label.pack(pady=10)

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

    columns = ("customer_ID","Name","contact_info", "Gender")
    table = ttk.Treeview(table_frame, columns=columns, show="headings")
    table.pack(fill=tk.BOTH, expand=True)

    for col in columns:
        table.heading(col, text=col)

    def fetch_data():
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
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

#admin_dashboard()