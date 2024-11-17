import tkinter as tk
from tkinter import messagebox
import mysql.connector
import os

# Connect to the MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="online_store"
)
cursor = db.cursor()

def register_user():
    name = name_entry.get()
    address = address_entry.get()
    contact_no = contact_entry.get()
    username = username_entry.get()
    password = password_entry.get()
    email = email_entry.get()

    if not (name and address and contact_no and username and password):
        messagebox.showerror("Error", "All fields are required")
        return

    # Insert into customers table to generate customerID
    insert_customer_query = """
    INSERT INTO customer (customerName, customerAddress, contactNo, email)
    VALUES (%s, %s, %s, %s)
    """
    customer_values = (name, address, contact_no, email)

    try:
        cursor.execute(insert_customer_query, customer_values)
        db.commit()
        customer_id = cursor.lastrowid  # Get the auto-generated customerID

        # Insert into customer_accs table
        insert_account_query = """
        INSERT INTO customer_accs (customerID, username, password, email)
        VALUES (%s, %s, %s, %s)
        """
        account_values = (customer_id, username, password, email)
        cursor.execute(insert_account_query, account_values)
        db.commit()

        messagebox.showinfo("Success", "Registration successful!")
        root.destroy()  # Close the sign-up window upon success
        os.system("python login.py")  # Open the login window from login.py

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Database error: {err}")

# Create the main sign-up window using Toplevel()
root = tk.Tk()
root.title("Sign Up Form")
root.geometry("1980x1020")
root.configure(bg="#D7E292")

signup_form_label = tk.Label(root, text="Sign Up Form", font=('Helvetica', 36, "bold"), bg="#D7E292")
signup_form_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

username_label = tk.Label(root, text="Username:", font=('Helvetica', 20), bg="#D7E292")
username_label.place(relx=0.3, rely=0.3, anchor=tk.W)

username_entry = tk.Entry(root, font=('Helvetica', 20), width=25)
username_entry.place(relx=0.4, rely=0.3, anchor=tk.W)

name_label = tk.Label(root, text="Name:", font=('Helvetica', 20), bg="#D7E292")
name_label.place(relx=0.3, rely=0.4, anchor=tk.W)

name_entry = tk.Entry(root, font=('Helvetica', 20), width=25)
name_entry.place(relx=0.4, rely=0.4, anchor=tk.W)

password_label = tk.Label(root, text="Password:", font=('Helvetica', 20), bg="#D7E292")
password_label.place(relx=0.3, rely=0.5, anchor=tk.W)

password_entry = tk.Entry(root, show="*", font=('Helvetica', 20), width=25)
password_entry.place(relx=0.4, rely=0.5, anchor=tk.W)

address_label = tk.Label(root, text="Address:", font=('Helvetica', 20), bg="#D7E292")
address_label.place(relx=0.3, rely=0.6, anchor=tk.W)

address_entry = tk.Entry(root, font=('Helvetica', 20), width=25)
address_entry.place(relx=0.4, rely=0.6, anchor=tk.W)

contact_label = tk.Label(root, text="Contact No:", font=('Helvetica', 20), bg="#D7E292")
contact_label.place(relx=0.3, rely=0.7, anchor=tk.W)

contact_entry = tk.Entry(root, font=('Helvetica', 20), width=25)
contact_entry.place(relx=0.4, rely=0.7, anchor=tk.W)

email_label = tk.Label(root, text="Email:", font=('Helvetica', 20), bg="#D7E292")
email_label.place(relx=0.3, rely=0.8, anchor=tk.W)

email_entry = tk.Entry(root, font=('Helvetica', 20), width=25)
email_entry.place(relx=0.4, rely=0.8, anchor=tk.W)

signup_button = tk.Button(root, text="Sign Up", width=10, font=('Helvetica', 16, "bold"), bg="#C3D45B", command=register_user)
signup_button.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

# Run the Tkinter main loop
root.mainloop()

# Close the database connection
db.close()
