import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
from admin import admin_dashboard
from customer import open_dashboard

root = tk.Tk()
root.title("Login")
root.geometry("600x400")

background_image = Image.open("bg1.jpg")
background_image = background_image.resize((600, 400), Image.LANCZOS)
background_photo = ImageTk.PhotoImage(background_image)

background_label = tk.Label(root, image=background_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
gender_var = tk.StringVar(value="Male")

def login():
    username = login_username_entry.get()
    password = login_password_entry.get()
    
    conn = sqlite3.connect("rent_a_car.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    
    
    if username == "admin" and password == "123":
        conn.close()
        root.destroy()                  # Close the login window
        admin_dashboard()               # Open the admin main page
        
    elif result:
        root.destroy()
        conn.close()         
        open_dashboard(username)        # Open the customer main page
    else:
        messagebox.showerror("Error", "Invalid username or password")
    
    conn.close()

def register():
    username = register_username_entry.get()
    password = register_password_entry.get()
    name     = register_name_entry.get()
    
    if username == "" or password == "" or name == "":
        messagebox.showerror("Error", "Please fill out both fields")
        return

    conn = sqlite3.connect("rent_a_car.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, name, password, Gender) VALUES (?, ?, ?, ?)", (username,name,password,gender_var.get()))
        conn.commit()
        messagebox.showinfo("Success", "Registration successful!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists")
    conn.close()

# Switch to the register frame
def show_register_frame():
    login_frame.pack_forget()
    register_frame.pack(side="left", padx=20, pady=20)

# Switch to the login frame
def show_login_frame():
    register_frame.pack_forget()
    login_frame.pack(side="left", padx=20, pady=50)


# Create frames for login and register
login_frame = tk.Frame(root, bg="white", padx=20, pady=20)
register_frame = tk.Frame(root, bg="white", padx=20, pady=20)

# Login Frame Widgets
tk.Label(login_frame, text="Login", font=("Arial", 20), bg="white").pack(pady=10)
tk.Label(login_frame, text="Username", bg="white").pack(anchor="w")
login_username_entry = tk.Entry(login_frame)
login_username_entry.pack()
tk.Label(login_frame, text="Password", bg="white").pack(anchor="w")
login_password_entry = tk.Entry(login_frame, show="*")
login_password_entry.pack()
tk.Button(login_frame, text="Login", command=login).pack(pady=10)
tk.Button(login_frame, text="Register", command=show_register_frame).pack()

# Register Frame Widgets
tk.Label(register_frame, text="Register", font=("Arial", 20), bg="white").pack(pady=10)
tk.Label(register_frame, text="Username", bg="white").pack(anchor="w")
register_username_entry = tk.Entry(register_frame)
register_username_entry.pack()
tk.Label(register_frame, text="Name", bg="white").pack(anchor="w")
register_name_entry = tk.Entry(register_frame)
register_name_entry.pack()
tk.Label(register_frame, text="Password", bg="white").pack(anchor="w")
register_password_entry = tk.Entry(register_frame, show="*")
register_password_entry.pack()
tk.Label(register_frame, text="Gender", bg="white").pack(anchor="w")

gender_frame = tk.Frame(register_frame, bg="white")
gender_frame.pack(anchor="w")
tk.Radiobutton(gender_frame, text="Male", variable=gender_var, value="Male", bg="white").pack(side="left")
tk.Radiobutton(gender_frame, text="Female", variable=gender_var, value="Female", bg="white").pack(side="left")


tk.Button(register_frame, text="Register", command=register).pack(pady=10)
tk.Button(register_frame, text="Back to Login", command=show_login_frame).pack()


show_login_frame()

root.mainloop()
