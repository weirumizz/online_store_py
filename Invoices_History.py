from tkinter import *
from tkinter import ttk, messagebox
import mysql.connector
import sys


class InvoiceHistoryApp:
    def __init__(self, master, customer_id):
        self.master = master
        self.master.title("Invoice History")
        self.master.geometry("1980x1020")  # Adjusted window size
        self.master.configure(bg="#D7E292")
        self.customer_id = customer_id

        # Establish database connection
        self.db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="online_store"
        )
        self.cursor = self.db_connection.cursor()

        # Background frame for Invoice History label
        self.title_frame = Frame(self.master, bg="#C3D45B", height=60)
        self.title_frame.pack(fill=X)

        # Title label
        self.label = Label(self.title_frame, text="Invoice History", font=("Inter", 20, 'bold'), bg="#C3D45B")
        self.label.pack(pady=10)

        # Entry and Search button on the right side
        self.E1 = Entry(self.master, width=35, font=("Inter", 10, 'bold'))
        self.E1.place(relx=0.83, rely=0.15, anchor=CENTER)

        self.search = Button(self.master, text="Search", font=("Inter", 10, 'bold'), command=self.search_invoices)
        self.search.place(relx=0.94, rely=0.15, anchor=CENTER)

        # Section label
        self.list_label = Label(self.master, text="INVOICE LIST", font=("Inter", 15, 'bold'), bg="#D7E292")
        self.list_label.place(relx=0.05, rely=0.2, anchor=NW)

        self.details_label = Label(self.master, text="INVOICE DETAILS", font=("Inter", 15, 'bold'), bg="#D7E292")
        self.details_label.place(relx=0.55, rely=0.2, anchor=NW)  # Adjusted placement

        # Invoice list with scrollbar using Listbox
        self.invoice_listbox = Listbox(self.master, width=40, height=20, font=("Inter", 12))
        self.invoice_listbox.place(relx=0.05, rely=0.25, anchor=NW)

        self.scrollbar1 = Scrollbar(self.master, orient=VERTICAL, command=self.invoice_listbox.yview)
        self.scrollbar1.place(relx=0.35, rely=0.25, relheight=0.5, anchor=NW)
        self.invoice_listbox.config(yscrollcommand=self.scrollbar1.set)

        # Example content for the invoice listbox
        self.fetch_invoices()  # Fetch invoices when the app starts

        # Invoice details with Text widget
        self.invoice_details_text = Text(self.master, width=50, height=30, font=("Inter", 12), state="normal")
        self.invoice_details_text.place(relx=0.55, rely=0.25, anchor=NW)  # Adjusted placement

        # Example content for the invoice details text widget
        self.invoice_details_text.insert(END, "Select an invoice from the list to display details.")

        # Total and Invoices labels and entry boxes
        self.total_label = Label(self.master, text="CUMULATIVE TOTAL:", font=("Inter", 12, 'bold'), bg="#D7E292")
        self.total_label.place(relx=0.05, rely=0.77, anchor=NW)

        self.total_entry = Entry(self.master, width=20, font=("Inter", 12, 'bold'), state="readonly")
        self.total_entry.place(relx=0.17, rely=0.77, anchor=NW)

        self.invoices_label = Label(self.master, text="INVOICES:", font=("Inter", 12, 'bold'), bg="#D7E292")
        self.invoices_label.place(relx=0.05, rely=0.81, anchor=NW)

        self.invoices_entry = Entry(self.master, width=20, font=("Inter", 12, 'bold'), state="readonly")
        self.invoices_entry.place(relx=0.17, rely=0.81, anchor=NW)

        # Delete, select, and submit buttons
        self.delete = Button(self.master, text="Delete", font=("Inter", 12, 'bold'), command=self.delete_invoice)
        self.delete.place(relx=0.05, rely=0.87, anchor=NW)

        self.select = ttk.Combobox(self.master, font=("Inter", 12, 'bold'), width=18, state='readonly')
        self.select.place(relx=0.17, rely=0.87, anchor=NW)
        self.select['values'] = ("Newest to Oldest", "Oldest to Newest")  # Sorting options
        self.select.current(0)  # Default to the first option

        self.submit = Button(self.master, text="Sort", font=("Inter", 12, 'bold'), command=self.sort_invoices)
        self.submit.place(relx=0.3, rely=0.87, anchor=NW)

        # Bind double-click event on listbox to display invoice details
        self.invoice_listbox.bind('<Double-Button-1>', self.on_invoice_select)

        # Count how many invoices for the logged in customer
        self.invoice_count()

        # Calculate cumulative total initially
        self.calculate_cumulative_total()

    def fetch_invoices(self):
        try:
            query = f"""
                SELECT invoiceID, date 
                FROM invoice 
                WHERE customerID = '{self.customer_id}'
                ORDER BY date DESC
                """

            self.cursor.execute(query)
            invoices = self.cursor.fetchall()

            # Clear existing items in the invoice listbox
            self.invoice_listbox.delete(0, END)

            # Insert fetched invoices into the invoice listbox
            for invoice in invoices:
                invoice_info = f"Invoice ID: {invoice[0]} - Date: {invoice[1]}"
                self.invoice_listbox.insert(END, invoice_info)

        except mysql.connector.Error as err:
            print(f"Error fetching invoices: {err}")

    def sort_invoices(self):
        sort_order = self.select.get()
        if sort_order == "Newest to Oldest":
            order_by = "DESC"
        else:
            order_by = "ASC"

        try:
            query = f"""
                SELECT invoiceID, date 
                FROM invoice 
                WHERE customerID = '{self.customer_id}'
                ORDER BY date {order_by}
                """

            self.cursor.execute(query)
            invoices = self.cursor.fetchall()

            # Clear existing items in the invoice listbox
            self.invoice_listbox.delete(0, END)

            # Insert sorted invoices into the invoice listbox
            for invoice in invoices:
                invoice_info = f"Invoice ID: {invoice[0]} - Date: {invoice[1]}"
                self.invoice_listbox.insert(END, invoice_info)

        except mysql.connector.Error as err:
            print(f"Error sorting invoices: {err}")

    def on_invoice_select(self, event):
        try:
            selected_index = self.invoice_listbox.curselection()
            if selected_index:
                selected_invoice = self.invoice_listbox.get(selected_index)
                invoice_id = selected_invoice.split(": ")[1].split(" -")[0]  # Extract invoice ID from selected text

                # Query database for invoice details and shipping method based on invoice_id
                query = (
                    "SELECT invoice.invoiceID, invoice.payment_method, invoice.date, invoice.total, invoice.customerID, "
                    "shipping_details.shipping_method "
                    "FROM invoice "
                    "LEFT JOIN shipping_details ON invoice.invoiceID = shipping_details.invoiceID "
                    "WHERE invoice.invoiceID = %s"
                )
                self.cursor.execute(query, (invoice_id,))
                invoice_details = self.cursor.fetchone()

                # Display details in the text widget
                if invoice_details:
                    details_text = (
                        "\n\t\tINVOICE DETAILS\n"
                        f"\nCustomer ID: {invoice_details[4]}\n"
                        f"\nInvoice ID: {invoice_details[0]}\n"
                        f"\nPayment Method: {invoice_details[1]}\n"
                        f"\nShipping Method: {invoice_details[5]}\n"  # Shipping method from the joined table
                        f"\nDate: {invoice_details[2]}\n"
                        f"\nTotal Cost: {invoice_details[3]}\n"
                        "\n\t\tThank you for purchasing!"
                    )
                    self.invoice_details_text.delete(1.0, END)
                    self.invoice_details_text.insert(END, details_text)

        except mysql.connector.Error as err:
            print(f"Error fetching invoice details: {err}")

    def delete_invoice(self):
        try:
            # Get the selected invoice index from the listbox
            selected_index = self.invoice_listbox.curselection()
            if selected_index:
                selected_invoice = self.invoice_listbox.get(selected_index)
                invoice_id = selected_invoice.split(": ")[1].split(" -")[0]  # Extract invoice ID from selected text

                # Delete shipping details associated with the invoice
                delete_shipping_query = "DELETE FROM shipping_details WHERE invoiceID = %s"
                self.cursor.execute(delete_shipping_query, (invoice_id,))

                # Delete invoice from database
                delete_invoice_query = "DELETE FROM invoice WHERE invoiceID = %s AND customerID = %s"
                self.cursor.execute(delete_invoice_query, (invoice_id, self.customer_id))
                self.db_connection.commit()

                # Remove invoice from listbox
                self.invoice_listbox.delete(selected_index)

                # Clear invoice details text widget
                self.invoice_details_text.delete(1.0, END)

                # Recalculate cumulative total after deletion
                self.calculate_cumulative_total()

                # Update invoice count after deletion
                self.invoice_count()

                messagebox.showinfo("Success", "Invoice deleted successfully.")

        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error deleting invoice and shipping details: {err}")

    def calculate_cumulative_total(self):
        try:
            query = f"""
                SELECT SUM(total) AS cumulative_total
                FROM invoice
                WHERE customerID = '{self.customer_id}'
                """

            self.cursor.execute(query)
            cumulative_total = self.cursor.fetchone()

            if cumulative_total and cumulative_total[0] is not None:
                self.total_entry.config(state="normal")
                self.total_entry.delete(0, END)
                self.total_entry.insert(0, cumulative_total[0])
                self.total_entry.config(state="readonly")
            else:
                self.total_entry.config(state="normal")
                self.total_entry.delete(0, END)
                self.total_entry.insert(0, "N/A")
                self.total_entry.config(state="readonly")

        except mysql.connector.Error as err:
            print(f"Error calculating cumulative total: {err}")

    def invoice_count(self):
        try:
            query = f"""
            SELECT COUNT(*) AS invoice_count
            FROM invoice
            WHERE customerID = '{self.customer_id}'
            """

            self.cursor.execute(query)
            invoice_count = self.cursor.fetchone()

            if invoice_count and invoice_count[0] is not None:
                self.invoices_entry.config(state="normal")
                self.invoices_entry.delete(0, END)
                self.invoices_entry.insert(0, invoice_count[0])
                self.invoices_entry.config(state="readonly")
            else:
                self.invoices_entry.config(state="normal")
                self.invoices_entry.delete(0, END)
                self.invoices_entry.insert(0, "N/A")
                self.invoices_entry.config(state="readonly")

        except mysql.connector.Error as err:
            print(f"Error calculating cumulative total: {err}")

    def search_invoices(self):
        search_invoice_id = self.E1.get().strip()
        if search_invoice_id:
            try:
                query = f"""
                    SELECT invoiceID, date 
                    FROM invoice 
                    WHERE customerID = '{self.customer_id}' AND invoiceID = '{search_invoice_id}'
                    """

                self.cursor.execute(query)
                invoice = self.cursor.fetchone()

                # Clear existing items in the invoice listbox
                self.invoice_listbox.delete(0, END)

                if invoice:
                    invoice_info = f"Invoice ID: {invoice[0]} - Date: {invoice[1]}"
                    self.invoice_listbox.insert(END, invoice_info)
                else:
                    messagebox.showinfo("No Results", "Invoice ID not found.")
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Error searching invoice: {err}")
        else:
            messagebox.showwarning("Input Error", "Please enter an Invoice ID to search.")


def main():
    if len(sys.argv) > 1:
        customer_id = sys.argv[1]
        print(customer_id)
    else:
        customer_id = "No customer ID provided"

    root = Tk()
    app = InvoiceHistoryApp(root, customer_id)
    root.mainloop()


if __name__ == "__main__":
    main()
