from tkinter import *
from tkinter import ttk, messagebox
import subprocess
import mysql.connector
from datetime import datetime
import sys

class MainW:
    def __init__(self, master):
        self.master = master
        self.master.geometry("1980x1020")
        self.master.title("TipidTipa")
        self.master.configure(bg="#D7E292")

        self.customer_id = customer_id

        # Initialize unit prices dictionary
        self.unit_prices = {
            "Bond Paper": {"Short": 1, "Long": 2},
            "Pencil": {"Standard": 7},
            "Pen": {"Standard": 9},
            "Ruler": {"Standard": 12},
            "Scissors": {"Standard": 30},
            "Eraser": {"Standard": 7},
            "Folder": {"Short": 4, "Long": 5},
            "Envelope": {"Short": 3, "Long": 4},
            "Notebook": {"Short": 12, "Long": 15}
        }

        # Initialize StringVars with initial values
        self.cust_id = StringVar(value=customer_id)
        self.cust_name = StringVar()
        self.cust_address = StringVar()
        self.cust_contact = StringVar()
        self.shipping_method = StringVar(value="")  # No selection initially
        self.payment_method = StringVar(value="")  # No selection initially
        self.subtotal_var = StringVar(value="$0.00")
        self.shipping_fee_var = StringVar(value="$38.00")
        self.total_var = StringVar(value="$0.00")

        # Retrieve customer information
        self.retrieve_customer_info()

        self.quantity_vars = []
        self.variety_comboboxes = []
        self.price_entries = []

    def retrieve_customer_info(self):
        try:
            # Connect to the database
            db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="online_store"
            )
            cursor = db.cursor()

            # Execute query to retrieve customer information
            query = """
            SELECT customerName, customerAddress, contactNo
            FROM customer
            WHERE customerID = %s
            """
            cursor.execute(query, (self.customer_id,))
            customer_data = cursor.fetchone()

            if customer_data:
                custN, custA, custNo = customer_data
                self.cust_name.set(custN)
                self.cust_address.set(custA)
                self.cust_contact.set(custNo)
            else:
                messagebox.showwarning("Warning", "Customer information not found.")

            # Close cursor and database connection
            cursor.close()
            db.close()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

        def compute_all():
            subtotal = 0
            for i, product in enumerate(products):
                quantity = self.quantity_vars[i].get()
                variety = self.variety_comboboxes[i].get()

                if quantity > 0 and variety in self.unit_prices.get(product, {}):
                    unit_price = self.unit_prices[product][variety]
                    total_price = unit_price * quantity
                    subtotal += total_price

                    # Update the price entry widget if quantity and variety are valid
                    if i < len(self.price_entries):
                        self.price_entries[i].config(state="normal")
                        self.price_entries[i].delete(0, END)
                        self.price_entries[i].insert(0, f"${total_price:.2f}")
                        self.price_entries[i].config(state="readonly")
                else:
                    # If quantity or variety is not specified, leave the price entry widget empty
                    if i < len(self.price_entries):
                        self.price_entries[i].config(state="normal")
                        self.price_entries[i].delete(0, END)
                        self.price_entries[i].config(state="readonly")

            self.subtotal_var.set(f"${subtotal:.2f}")

            if self.shipping_method.get() == "Delivery":
                self.shipping_fee_var.set("$38.00")
                total = subtotal + 38  # Adding a fixed shipping fee for demonstration
                self.total_var.set(f"${total:.2f}")
            else:
                self.shipping_fee_var.set("")
                total = subtotal
                self.total_var.set(f"${total:.2f}")

        def open_invoice():
            subprocess.run(["python", "Invoices_History.py", str(customer_id)])

        def check_action(var, combobox):
            if var.get():
                combobox.config(state="readonly")
            else:
                combobox.config(state="disabled")

        def submit_action():
            confirmation = messagebox.askyesno("Confirm Submit", "Are you sure you want to submit?")
            if confirmation:
                try:
                    # Connect to the database
                    db = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        password="root",
                        database="online_store"
                    )
                    cursor = db.cursor()

                    # Insert into orders table
                    for i, product in enumerate(products):
                        if i < len(self.quantity_vars):  # Check if i is within bounds
                            quantity = int(self.quantity_vars[i].get())
                            variety = self.variety_comboboxes[i].get()
                            if quantity > 0:
                                product_id = i + 1  # Assuming product IDs start from 1
                                # Prepare order data
                                order_data = (
                                    quantity,  # Quantity of the product
                                    self.unit_prices[product][variety],  # Cost of the product
                                    int(self.cust_id.get()),  # Customer ID (convert to int)
                                    product_id  # Product ID
                                )
                                # SQL query to insert into orders table
                                insert_order_query = "INSERT INTO orders (quantity, cost, customerID, productID) VALUES (%s, %s, %s, %s)"
                                cursor.execute(insert_order_query, order_data)
                                db.commit()
                                print(f"Order inserted: {order_data}")  # Print for debugging

                    # Insert into invoices table
                    invoice_data = (
                        self.payment_method.get(),  # Payment method
                        datetime.now(),  # Current date and time
                        float(self.total_var.get()[1:]),  # Total amount (remove '$' and convert to float)
                        int(self.cust_id.get())  # Customer ID (convert to int)
                    )
                    insert_invoice_query = "INSERT INTO invoice (payment_method, date, total, customerID) VALUES (%s, %s, %s, %s)"
                    cursor.execute(insert_invoice_query, invoice_data)
                    db.commit()
                    invoice_id = cursor.lastrowid  # Get the last inserted invoiceID
                    print(f"Invoice inserted: {invoice_data}, InvoiceID: {invoice_id}")  # Print for debugging

                    # Insert into shipping_details table
                    shipping_data = (
                        invoice_id,  # Invoice ID
                        int(self.cust_id.get()),  # Customer ID
                        self.shipping_method.get()  # Shipping method
                    )
                    insert_shipping_query = "INSERT INTO shipping_details (invoiceID, customerID, shipping_method) VALUES (%s, %s, %s)"
                    cursor.execute(insert_shipping_query, shipping_data)
                    db.commit()
                    print(f"Shipping details inserted: {shipping_data}")  # Print for debugging

                    # Open a new window indicating invoice recorded
                    messagebox.showinfo("Invoice Recorded", "The invoice has been recorded successfully.")
                    reset_all()  # Call reset_all from within the class

                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Error: {err}")

                finally:
                    # Close the cursor and database connection
                    cursor.close()
                    db.close()

        def reset_all():
            for var, combobox, quantity_var in zip(self.checkbox_vars, self.variety_comboboxes, self.quantity_vars):
                if combobox.get() != "Standard":
                    var.set(0)  # Reset checkbox state
                    combobox.set("")  # Reset combobox selection
                    combobox.config(state="disabled")  # Ensure combobox is disabled
                else:
                    var.set(0)
                    combobox.config(state="disabled")
                quantity_var.set(0)

            self.shipping_method.set(1)  # Reset shipping method selection
            self.payment_method.set(1)  # Reset payment method selection
            self.subtotal_var.set("$0.00")  # Reset subtotal
            self.shipping_fee_var.set("")  # Reset shipping fee
            self.total_var.set("$0.00")  # Reset total

            for entry in self.price_entries:
                entry.config(state="normal")
                entry.delete(0, END)
                entry.config(state="readonly")

        # Add labels and read-only entry widgets for customer information

        Label(self.master, text="CUSTOMER INFORMATION", bg="#D7E292", fg="black",
              font=("Comic Sans", 15, "bold")).grid(row=1, column=0, columnspan=2, sticky=W)

        Label(self.master, text="Customer ID", bg="#D7E292", fg="black",
              font=("Comic Sans", 10, "bold")).grid(row=2, column=0, sticky=W)
        Entry(self.master, textvariable=self.cust_id, bg="#D7E292", fg="black",
              font=("Comic Sans", 10, "bold"), state="readonly", width=50).grid(row=2, column=1, sticky=W)

        Label(self.master, text="Customer Name", bg="#D7E292", fg="black",
              font=("Comic Sans", 10, "bold")).grid(row=3, column=0, sticky=W)
        Entry(self.master, textvariable=self.cust_name, bg="#D7E292", fg="black",
              font=("Comic Sans", 10, "bold"), state="readonly", width=50).grid(row=3, column=1, sticky=W)

        Label(self.master, text="Address", bg="#D7E292", fg="black",
              font=("Comic Sans", 10, "bold")).grid(row=4, column=0, sticky=W)
        Entry(self.master, textvariable=self.cust_address, bg="#D7E292", fg="black",
              font=("Comic Sans", 10, "bold"), state="readonly", width=50).grid(row=4, column=1, sticky=W)

        Label(self.master, text="Contact Number", bg="#D7E292", fg="black",
              font=("Comic Sans", 10, "bold")).grid(row=5, column=0, sticky=W)
        Entry(self.master, textvariable=self.cust_contact, bg="#D7E292", fg="black",
              font=("Comic Sans", 10, "bold"), state="readonly", width=50).grid(row=5, column=1, sticky=W)

        # Add products ordered section
        Label(self.master, text="\nPRODUCTS ORDERED", bg="#D7E292", fg="black",
              font=("Comic Sans", 15, "bold")).grid(row=7, column=1, columnspan=5, sticky=W)

        Label(self.master, text="ITEM", bg="#D7E292", fg="black",
              font=("Comic Sans", 12, "bold")).grid(row=8, column=1, padx=10)
        Label(self.master, text="VARIETY", bg="#D7E292", fg="black",
              font=("Comic Sans", 12, "bold")).grid(row=8, column=2, padx=10)
        Label(self.master, text="QUANTITY", bg="#D7E292", fg="black",
              font=("Comic Sans", 12, "bold")).grid(row=8, column=3, padx=10)
        Label(self.master, text="PRICE", bg="#D7E292", fg="black",
              font=("Comic Sans", 12, "bold")).grid(row=8, column=4, padx=10)

        # List of products
        products = ["Bond Paper", "Pencil", "Pen", "Ruler", "Scissors", "Eraser", "Folder", "Envelope", "Notebook"]
        variety_options = ["Short", "Long"]
        special_items = {"Bond Paper", "Folder", "Envelope", "Notebook"}

        # Create checkboxes, comboboxes, and quantity controls for each product
        # Initialize lists to hold variables and widgets
        self.quantity_vars = []
        self.variety_comboboxes = []
        self.price_entries = []

        # Create checkboxes, comboboxes, and quantity controls for each product
        self.checkbox_vars = []

        for i, product in enumerate(products, start=9):
            var = IntVar()
            self.checkbox_vars.append(var)  # Store the checkbox IntVar

            combobox = ttk.Combobox(self.master, values=variety_options, state="disabled")
            if product in special_items:
                combobox.grid(row=i, column=2, padx=10)
            else:
                combobox = ttk.Combobox(self.master, state="disabled")
                combobox.set("Standard")
                combobox.grid(row=i, column=2, padx=10)

            Checkbutton(self.master, text=product, variable=var, bg="#D7E292", fg="black",
                        font=("Comic Sans", 12, "bold"), command=lambda v=var, cb=combobox: check_action(v, cb)).grid(
                row=i, column=1, sticky=W, padx=10)

            quantity_var = IntVar(value=0)
            Spinbox(self.master, textvariable=quantity_var, from_=0, to=100).grid(row=i, column=3, padx=10)
            self.quantity_vars.append(quantity_var)

            # Append the combobox to the list
            self.variety_comboboxes.append(combobox)

            price_entry = Entry(self.master, width=10, state="readonly")
            price_entry.grid(row=i, column=4, padx=10)
            self.price_entries.append(price_entry)

        # Add shipping method section
        self.shipping_method.set(1)
        Label(self.master, text="\nSHIPPING METHOD", bg="#D7E292", fg="black",
              font=("Comic Sans", 12, "bold")).grid(row=18, column=1, columnspan=4, sticky=W)

        Radiobutton(self.master, text="Delivery", variable=self.shipping_method, value="Delivery",
                    bg="#D7E292", fg="black", font=("Comic Sans", 10, "bold")).grid(row=19, column=1, sticky=W,
                                                                                       padx=10)

        Radiobutton(self.master, text="Pick-Up", variable=self.shipping_method, value="Pick-Up",
                    bg="#D7E292", fg="black", font=("Comic Sans", 10, "bold")).grid(row=19, column=2, sticky=W,
                                                                                       padx=10)

        # Add payment method section
        self.payment_method.set(1)
        Label(self.master, text="\nPAYMENT METHOD", bg="#D7E292", fg="black",
              font=("Comic Sans", 12, "bold")).grid(row=20, column=1, columnspan=4, sticky=W)

        Radiobutton(self.master, text="Debit/Credit", variable=self.payment_method, value="Debit/Credit",
                    bg="#D7E292", fg="black", font=("Comic Sans", 10, "bold")).grid(row=21, column=1, sticky=W,
                                                                                       padx=10)

        Radiobutton(self.master, text="Cash on Delivery", variable=self.payment_method, value="Cash on Delivery",
                    bg="#D7E292", fg="black", font=("Comic Sans", 10, "bold")).grid(row=21, column=2, sticky=W,
                                                                                       padx=10)

        Radiobutton(self.master, text="GCash", variable=self.payment_method, value="GCash",
                    bg="#D7E292", fg="black", font=("Comic Sans", 10, "bold")).grid(row=22, column=1, sticky=W,
                                                                                       padx=10)

        Radiobutton(self.master, text="Maya", variable=self.payment_method, value = "Maya",
                    bg="#D7E292", fg="black", font=("Comic Sans", 10, "bold")).grid(row=22, column=2, sticky=W,
                                                                                       padx=10)

        # Add subtotal section
        Label(self.master, text="\nSUBTOTAL: ", bg="#D7E292", fg="black",
              font=("Comic Sans", 12, "bold")).grid(row=20, column=3, sticky=E)

        Entry(self.master, textvariable=self.subtotal_var, width=10, state="readonly").grid(row=20, column=4, sticky=E)

        # Add shipping fee section
        Label(self.master, text="SHIPPING FEE: ", bg="#D7E292", fg="black",
              font=("Comic Sans", 12, "bold")).grid(row=21, column=3, sticky=E)

        Entry(self.master, textvariable=self.shipping_fee_var, width=10).grid(row=21, column=4, sticky=E)

        # Add total section
        Label(self.master, text="TOTAL: ", bg="#D7E292", fg="black",
              font=("Comic Sans", 12, "bold")).grid(row=22, column=3, sticky=E)

        Entry(self.master, textvariable=self.total_var, width=10, state="readonly").grid(row=22, column=4, sticky=E)

        # Add compute button
        Button(self.master, text="Compute", bg="#D7E292", fg="black", font=("Comic Sans", 12, "bold"), command=compute_all).grid(row=23, column=3, sticky=E, pady=10)

        # Add submit button
        Button(self.master, text="Submit", bg="#D7E292", fg="black", font=("Comic Sans", 12, "bold"), command=submit_action).grid(row=23, column=4, sticky=E, pady=10)

        # Add button to open invoice history window
        Button(self.master, text="Invoice History", command=open_invoice, bg="#D7E292", fg="black",
               font=("Comic Sans", 12, "bold")).grid(row=23, column=1, columnspan=2, sticky=W, pady=10)

        # Start the Tkinter event loop
        self.master.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        customer_id = sys.argv[1]
        print(customer_id)
    else:
        customer_id = "No customer ID provided"
    root = Tk()
    app = MainW(root)
    root.mainloop()