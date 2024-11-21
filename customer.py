import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from PIL import Image, ImageTk
from tkinter import messagebox
import sqlite3
from datetime import datetime

def open_dashboard(username):
    root = tk.Tk()
    root.title("Customer Dashboard")
    root.geometry("600x400")

    background_image = Image.open("bg2.jpg")
    background_image = background_image.resize((600, 400), Image.LANCZOS)
    background_photo = ImageTk.PhotoImage(background_image)

    background_label = tk.Label(root, image=background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    conn = sqlite3.connect("rent_a_car.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM users WHERE username = ?", (username,))
    name=cursor.fetchone()
    welcome_label = tk.Label(root, text=f"Welcome, {name[0]}!", font=("Arial", 16), bg="lightblue", fg="black")
    welcome_label.place(x=0, y=0, width=600, height=30)
    
    cursor.execute("SELECT vehicle_ID, brand, price_per_day FROM cars WHERE in_maintenance = 0 AND reserved = 0")
    available_cars = cursor.fetchall()

    def discount():
        
        car_selection = car_dropdown.get()
        car_id = car_selection.split(" - ")[0]
        start_date = datetime.strptime(start_calendar.get(), "%m/%d/%y")
        end_date = datetime.strptime(end_calendar.get(), "%m/%d/%y")
        days = (end_date - start_date).days
        
        cursor.execute("SELECT customer_ID FROM users WHERE username = ?", (username,))
        customer_id=cursor.fetchone()

        price_per_day = car_prices[car_id] if car_id in car_prices else 0
        total_price = days * price_per_day

        cursor.execute("SELECT discount_code FROM discounts WHERE customer_ID = ?", (customer_id[0],))
        discount_row = cursor.fetchone()

        if not discount_row:
            messagebox.showerror("Error"," No discount available")
            return

        discount_code = discount_row[0]
        discounted_price = total_price - (discount_code * total_price)/100

        total_price_label.config(text=f"Total Price: ₹{discounted_price}")

    
    def update_total_price():
        try:
            car_selection = car_dropdown.get()
            car_id = car_selection.split(" - ")[0]
            start_date = datetime.strptime(start_calendar.get(), "%m/%d/%y")
            end_date = datetime.strptime(end_calendar.get(), "%m/%d/%y")
            days = (end_date - start_date).days
            price_per_day = car_prices[car_id] if car_id in car_prices else 0
            total_price = int(days * price_per_day)
            total_price_label.config(text=f"Total Price: ₹{total_price}")
        except Exception as e:
            total_price_label.config(text="Total Price ₹0")

    def reserve_car():
        try:
            car_selection = car_dropdown.get()
            car_id = car_selection.split(" - ")[0]
            start_date = start_calendar.get()
            end_date = end_calendar.get()
            
            start_date_formatted = datetime.strptime(start_date, "%m/%d/%y").strftime("%Y-%m-%d")
            end_date_formatted = datetime.strptime(end_date, "%m/%d/%y").strftime("%Y-%m-%d")
            
            if car_id != "" and start_date != "" and end_date != "":
                cursor.execute("SELECT customer_ID FROM users WHERE username = ?", (username,))
                customer_id=cursor.fetchone()
                cursor.execute('''
                INSERT INTO reservations (customer_ID, car_id, start_date, end_date)
                VALUES (?, ?, ?, ?)
                ''', (customer_id[0], car_id, start_date_formatted, end_date_formatted))

                conn.commit()
                messagebox.showinfo("Reservation", "Reservation successfully added!")
                
        except sqlite3.Error as e:
            conn.rollback()
            messagebox.showerror("Error", f"Database error: {e}")
    
    # Mapping car IDs to prices
    car_prices = {car[0]: car[2] for car in available_cars}
    
    car_dropdown_label = tk.Label(root, text="Select Car", font=("Arial", 12), bg="lightblue", fg="black")
    car_dropdown_label.place(x=5, y=50)
    car_dropdown = ttk.Combobox(root, values=[f"{car[0]} - {car[1]}" for car in available_cars])
    car_dropdown.place(x=100, y=50)

    start_date_label = tk.Label(root, text="Start Date", font=("Arial", 12), bg="lightblue", fg="black")
    start_date_label.place(x=5, y=100)
    start_calendar = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
    start_calendar.place(x=90, y=100)

    end_date_label = tk.Label(root, text="End Date", font=("Arial", 12), bg="lightblue", fg="black")
    end_date_label.place(x=5, y=150)
    end_calendar = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
    end_calendar.place(x=90, y=150)

    total_price_label = tk.Label(root, text="Total Price ₹0", font=("Arial", 14), bg="lightblue", fg="black")
    total_price_label.place(x=5, y=200)

    calculate_button = tk.Button(root, text="Calculate Total Price", command=update_total_price)
    calculate_button.place(x=5, y=250)
    
    discount_button = tk.Button(root, text="Discount", command=discount)
    discount_button.place(x=140, y=250)
    
    reserve_button = tk.Button(root, text="Reserve", command=reserve_car)
    reserve_button.place(x=200, y=250)

    root.mainloop()
    conn.close()
