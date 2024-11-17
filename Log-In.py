import tkinter as tk
from tkinter import messagebox
import mysql.connector
import subprocess

# Connect to the MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="online_store"
)
cursor = db.cursor()

# Function to retrieve customer_id using username
def open_signup():
    subprocess.run(["python", "Sign-Up.py"])
def get_customer_id(username):
    query = """
    SELECT customer.customerID FROM customer
    INNER JOIN customer_accs ON customer.customerID = customer_accs.customerID
    WHERE customer_accs.username = %s
    """
    cursor.execute(query, (username,))
    result = cursor.fetchone()

    if result:
        return result[0]  # Return customerID
    else:
        return None

# Function to handle login button click
def login_user():
    username = username_entry.get()
    password = password_entry.get()

    # Validate username and password (optional)

    # Retrieve customerID based on username
    customer_id = get_customer_id(username)

    if customer_id:
        messagebox.showinfo("Success", f"Login successful! \nCustomer ID: {customer_id}")
        root.destroy()
        subprocess.run(["python", "Order_Form.py", str(customer_id)])
        # You can store customer_id in a global variable or use it as needed
    else:
        messagebox.showerror("Error", "Invalid username")

# Create the main login window
# Create the main login window using pack
root = tk.Tk()
root.title("Login Form")
root.geometry("1980x1020")
root.configure(bg="#D7E292")

login_form_label = tk.Label(root, text="Log In Form", font=('Helvetica', 36, "bold"), bg="#D7E292")
login_form_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

name_label = tk.Label(root, text="Username:", font=('Helvetica', 20, "bold"), bg="#D7E292")
name_label.place(relx=0.3, rely=0.3, anchor=tk.W)

username_entry = tk.Entry(root, font=('Helvetica', 24))
username_entry.place(relx=0.4, rely=0.3, anchor=tk.W)

password_label = tk.Label(root, text="Password:", font=('Helvetica', 20, "bold"), bg="#D7E292")
password_label.place(relx=0.3, rely=0.4, anchor=tk.W)

password_entry = tk.Entry(root, show="*", font=('Helvetica', 24))
password_entry.place(relx=0.4, rely=0.4, anchor=tk.W)

login_button = tk.Button(root, text="Log In", width=20, font=('Helvetica', 20, "bold"), bg="#C3D45B", command=login_user)
login_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

signup_button = tk.Button(root, text="Sign Up", width=20, font=('Helvetica', 20, "bold"), bg="#C3D45B", command=open_signup)
signup_button.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

root.mainloop()

# Close the database connection
db.close()
