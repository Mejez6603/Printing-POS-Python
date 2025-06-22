import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkinter import messagebox
import csv
import os
from tkinter import filedialog
from transaction import save_records_to_csv, load_records_from_csv, validate_integer, validate_float
from sales_report import generate_daily_sales_report, generate_monthly_sales_report
# We only need open_sales_report_window for the Toplevel option in main.py for now
from sales_report_window import open_sales_report_window
from PIL import Image, ImageTk # Still needed for the logo

selected_item = None  # Track currently edited item (global, as in original setup)

# Global lists/variables used in functions
entries = []
pages_var = None
price_var = None
total_var = None
record_table = None
item_table = None
btn_additem = None
btn_confirm = None
lbl_today_income = None
lbl_today_date = None
lbl_month_income = None
lbl_month_date = None
lbl_year_income = None
lbl_year_date = None
item_menu = None
record_menu = None


# --- Functions (Converted back to global functions as in original main.py) ---
def validate_entries(*args):
    global btn_additem, entries
    if all(entry.get() for entry in entries):
        btn_additem.config(state="normal")
    else:
        btn_additem.config(state="disabled")

def suggest_total_price(*args):
    global pages_var, price_var, total_var
    try:
        pages = int(pages_var.get())
        price_per_page = float(price_var.get())
        suggested_total = pages * price_per_page

        #if total_var.get() == "":
        total_var.set(f"{suggested_total:.2f}")

    except ValueError:
        #if total_var.get() == "":
        total_var.set("")

def add_item():
    global selected_item, entries, item_table, btn_additem
    values = [entry.get() for entry in entries]

    if all(values):
        try:
            int(values[2])
            float(values[3])
            float(values[4])
        except ValueError:
            messagebox.showerror("Invalid Input", "Pages, Price/Page, and Total must be numbers.")
            return

        if selected_item:  # Editing existing item
            item_table.item(selected_item, values=values)
            selected_item = None
            btn_additem.config(text="Add Item")
        else:  # Adding new
            item_table.insert("", "end", values=values)

        for entry in entries:
            entry.delete(0, tk.END)

        btn_additem.config(state="disabled")
    else:
        messagebox.showwarning("Incomplete Fields", "Please fill in all fields.")


def confirm_transaction():
    global item_table, record_table, btn_confirm
    if not item_table.get_children():
        messagebox.showwarning("Incomplete", "Complete the information before confirming transaction.")
        return

    now = datetime.now()
    transaction_id = f"TRX-{now.strftime('%Y%m%d-%H%M%S')}"
    date = now.strftime("%m/%d/%Y")
    time_now = now.strftime("%I:%M%p")

    for child in item_table.get_children():
        values = item_table.item(child)['values']
        record_table.insert("", 0, values=(transaction_id, date, time_now, *values))

    item_table.delete(*item_table.get_children())

    # 📌 Auto-save after confirming
    save_records_to_csv(record_table)

    update_sales_summary()

def on_item_click(event):
    global selected_item, item_table, entries, btn_additem
    item_id = item_table.identify_row(event.y)
    col = item_table.identify_column(event.x)

    if item_id:
        col_index = int(col.replace('#', '')) - 1
        values = item_table.item(item_id, 'values')

        if col_index == len(values):  # Delete
            if messagebox.askyesno("Delete", "Delete this item?"):
                item_table.delete(item_id)
                selected_item = None
                clear_entry_fields()
                btn_additem.config(text="Add Item", state="disabled")
        elif col_index == len(values) - 1:  # Edit (if clicking on last column to edit)
            populate_entries_for_edit(values, item_id)
        else: # Any other click on item implies intent to edit
            populate_entries_for_edit(values, item_id)

def populate_entries_for_edit(values, item_id):
    global selected_item, entries, btn_additem
    selected_item = item_id
    for i, val in enumerate(values):
        if i < len(entries): # Safety check for list bounds
            entries[i].delete(0, tk.END)
            entries[i].insert(0, val)
    btn_additem.config(text="Update Item", state="normal")

def clear_entry_fields():
    global entries
    for entry in entries:
        entry.delete(0, tk.END)

def on_item_double_click(event):
    global selected_item, item_table
    item_id = item_table.identify_row(event.y)
    if item_id:
        values = item_table.item(item_id, 'values')
        populate_entries_for_edit(values, item_id)

def on_item_right_click(event):
    global selected_item, item_table, item_menu
    row_id = item_table.identify_row(event.y)
    if row_id:
        item_table.selection_set(row_id)
        selected_item = row_id
        item_menu.post(event.x_root, event.y_root)

def edit_selected_item():
    global selected_item, item_table
    if selected_item:
        values = item_table.item(selected_item, 'values')
        populate_entries_for_edit(values, selected_item)

def delete_selected_item():
    global selected_item, item_table, btn_additem
    if selected_item:
        if messagebox.askyesno("Delete", "Delete this item?"):
            item_table.delete(selected_item)
            selected_item = None
            clear_entry_fields()
            btn_additem.config(text="Add Item", state="disabled")

def on_record_right_click(event):
    global selected_item, record_table, record_menu
    row_id = record_table.identify_row(event.y)
    if row_id:
        record_table.selection_set(row_id)
        selected_item = row_id
        record_menu.post(event.x_root, event.y_root)

def delete_selected_record():
    global selected_item, record_table
    if selected_item:
        if messagebox.askyesno("Delete", "Delete this transaction?"):
            record_table.delete(selected_item)
            selected_item = None
            save_records_to_csv(record_table)
            update_sales_summary()

def edit_selected_record():
    messagebox.showinfo("Notice", "Edit not available, manage items before confirming.")

def update_sales_summary():
    global lbl_today_income, lbl_today_date, lbl_month_income, lbl_month_date, lbl_year_income, lbl_year_date
    today = datetime.now().strftime("%m/%d/%Y")
    month = datetime.now().strftime("%m/%Y")
    year = datetime.now().strftime("%Y")

    today_total = generate_daily_sales_report(today)
    month_total = generate_monthly_sales_report(month)
    year_total = sum([generate_monthly_sales_report(f"{m:02}/{year}") for m in range(1, 13)])

    lbl_today_income.config(text=f"Today's Income: ₱{today_total:.2f}")
    lbl_today_date.config(text=f"({today})")

    lbl_month_income.config(text=f"This Month: ₱{month_total:.2f}")
    lbl_month_date.config(text=f"({month})")

    lbl_year_income.config(text=f"This Year: ₱{year_total:.2f}")
    lbl_year_date.config(text=f"({year})")

def update_datetime():
    global datetime_label
    now = datetime.now()
    current_time = now.strftime("%m/%d/%Y — %I:%M %p")
    datetime_label.config(text=current_time)
    # Compute milliseconds until the start of the next minute
    next_minute = (60 - now.second) * 1000 - now.microsecond // 1000

    root.after(next_minute, update_datetime)

def reset_records_csv():
    global record_table # Access the global record_table
    # Access global summary labels to update them
    global lbl_today_income, lbl_today_date, lbl_month_income, lbl_month_date, lbl_year_income, lbl_year_date

    # Define the path to your records.csv file
    # This path should be consistent with how transaction.py accesses it
    file_path = os.path.join("database", "records.csv")

    # Confirmation dialog before proceeding
    if messagebox.askyesno("Confirm Reset", "Are you sure you want to delete ALL sales records?\nThis action cannot be undone."):
        try:
            # Check if the file exists before trying to delete it
            if os.path.exists(file_path):
                os.remove(file_path)
                messagebox.showinfo("Reset Complete", "All sales records have been successfully deleted.")
            else:
                messagebox.showinfo("Reset Info", "No records file found. The system is already in a fresh state.")

            # Clear all entries from the Treeview in the GUI
            record_table.delete(*record_table.get_children())

            # Update the quick sales summary to reflect zero values
            update_sales_summary() # Call your existing function to refresh the summary labels

        except OSError as e:
            # Handle potential errors during file deletion (e.g., file in use, permission issues)
            messagebox.showerror("Error", f"Could not delete records file: {e}\nPlease ensure the file is not open and you have write permissions.")
    else:
        # User cancelled the reset operation
        messagebox.showinfo("Reset Cancelled", "Sales record reset was cancelled.")

# --- Initialize main window ---
root = tk.Tk()
root.title("Printing Shop Transaction System")
root.geometry("1000x600")
root.resizable(False, False)

# --- Add this section to replace the window icon ---
try:
    # 1. Define the path to your new window icon file.
    #    Make sure your icon file (e.g., 'my_app_icon.png') is in the same directory as main.py
    #    Or adjust the path, e.g., os.path.join(os.path.dirname(__file__), "images", "my_app_icon.png")
    window_icon_file = os.path.join(os.path.dirname(__file__),
                                    "your_app_icon.png")  # <--- CHANGE 'your_app_icon.png' to your actual file name

    # 2. Load the image using Pillow (PIL)
    #    Common formats are .png, .gif. .ico works too.
    icon_image = Image.open(window_icon_file)

    # 3. (Optional) Resize the image for optimal display in the title bar.
    #    Typical sizes are 16x16, 24x24, 32x32. If your image is very large, resizing is good.
    # icon_image = icon_image.resize((32, 32), Image.LANCZOS) # Uncomment and adjust size if needed

    # 4. Convert to ImageTk.PhotoImage for Tkinter
    tk_icon_photo = ImageTk.PhotoImage(icon_image)

    # 5. Set the window icon.
    #    The 'True' argument means this icon will also apply to any Toplevel windows (like your Sales Report).
    root.iconphoto(True, tk_icon_photo)

except FileNotFoundError:
    print(f"Window icon file not found at {window_icon_file}. Using default system icon.")
except Exception as e:
    print(f"An error occurred loading the window icon: {e}. Using default system icon.")

# === Top Date and Time Label ===
datetime_label = tk.Label(root, text="", font=("Arial", 10))
datetime_label.place(x=800, y=10)
update_datetime() # Start datetime updates

# Validation commands (need to be registered with the root window)
vcmd_int = (root.register(validate_integer), '%P')
vcmd_float = (root.register(validate_float), '%P')

# === Left Sidebar ===
sidebar = tk.Frame(root, bg="white", width=150, height=600, relief="solid", bd=1)
sidebar.place(x=0, y=0)

# --- Add Image/Logo to Sidebar ---
try:
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    img = Image.open(logo_path)
    img = img.resize((40, 40), Image.LANCZOS) # Example resize
    logo_photo = ImageTk.PhotoImage(img) # Keep reference
    logo_label = tk.Label(sidebar, image=logo_photo, bg="white")
    logo_label.place(x=45, y=20) # Adjust x, y for desired padding/centering
except FileNotFoundError:
    print(f"Error: Logo file not found at {logo_path}. Skipping logo display.")
    logo_label = tk.Label(sidebar, text="Logo Missing", bg="white", fg="red")
    logo_label.place(x=15, y=10)
except Exception as e:
    print(f"An error occurred loading the logo: {e}")
    logo_label = tk.Label(sidebar, text="Error Loading Logo", bg="white", fg="red")
    logo_label.place(x=15, y=10)

# Sidebar Buttons
# Adjust button Y positions to be below the logo based on logo's height
logo_display_height = logo_photo.height() if 'logo_photo' in locals() else 0
button_start_y = 10 + logo_display_height + 20 # 10 (logo_y) + logo_height + 20 (padding)
if logo_display_height == 0: # Fallback if no logo loaded/failed
    button_start_y = 20

#btn_transaction = tk.Button(sidebar, text="Transaction", height=2, width=15)
#btn_transaction.place(x=10, y=button_start_y) # Revert to simple Y placement

btn_report = tk.Button(sidebar, text="Report", height=2, width=15)
btn_report.place(x=10, y=button_start_y + 20) # Revert to simple Y placement

# Single-click opens the Toplevel window (Option 1)
btn_report.config(command=lambda: open_sales_report_window(root))
# Double-click binding removed for now, as we're postponing embedded view

btn_soon = tk.Button(sidebar, text="(soon)", height=2, width=15, state="disabled")
btn_soon.place(x=10, y=button_start_y + 80) # Revert to simple Y placement

# Reset Button
# Position it towards the bottom left of the sidebar
btn_reset = tk.Button(sidebar, text="Reset Records", height=2, width=15, bg="darkred", fg="white", command=reset_records_csv)
btn_reset.place(x=10, y=550) # y=550 should place it near the bottom of the 600px tall window, adjust if needed

# === Transaction Section ===
lbl_transaction = tk.Label(root, text="Transaction", font=("Arial", 16))
lbl_transaction.place(x=180, y=10)

transaction_frame = tk.Frame(root, bg="white", width=800, height=80, relief="solid", bd=1)
transaction_frame.place(x=180, y=40)

# === Item List Section ===
lbl_itemlist = tk.Label(root, text="Items in Transaction", font=("Arial", 12))
lbl_itemlist.place(x=180, y=120)

itemlist_frame = tk.Frame(root, bg="white", width=800, height=150, relief="solid", bd=1)
itemlist_frame.place(x=180, y=145)

# Treeview for Item List
item_columns = ("Paper Type", "Color", "Pages", "Price/Page", "Total")
item_table = ttk.Treeview(itemlist_frame, columns=item_columns, show="headings", height=6)

for col in item_columns:
    item_table.heading(col, text=col)
    item_table.column(col, width=130, anchor="center")

item_table.grid(row=0, column=0, sticky="nsew")
item_table.bind("<Button-1>", on_item_click)
item_table.bind("<Double-1>", on_item_double_click)
item_table.bind("<Button-3>", on_item_right_click)

item_menu = tk.Menu(root, tearoff=0)
item_menu.add_command(label="Edit Item", command=edit_selected_item)
item_menu.add_command(label="Delete Item", command=delete_selected_item)

# Scrollbar beside it
item_scroll = ttk.Scrollbar(itemlist_frame, orient="vertical", command=item_table.yview)
item_table.configure(yscroll=item_scroll.set)
item_scroll.grid(row=0, column=1, sticky="ns")

# Allow frame to expand properly
itemlist_frame.grid_rowconfigure(0, weight=1)
itemlist_frame.grid_columnconfigure(0, weight=1)

# Transaction Headers
headers = ["ID", "Date", "Time", "Paper Type", "Color", "Pages", "Price/Page", "Total"]
for i, header in enumerate(headers):
    lbl = tk.Label(transaction_frame, text=header, font=("Arial", 10, "bold"), bg="white")
    lbl.grid(row=0, column=i, padx=5, pady=5)

# Entry Widgets (Only for columns 3 to 7)
# Global entries list will be populated here
entries = []

# Paper Type (Dropdown)
paper_type_var = tk.StringVar()
paper_type_var.trace_add("write", validate_entries)
paper_type_combo = ttk.Combobox(transaction_frame, width=10, textvariable=paper_type_var, state="readonly")
paper_type_combo['values'] = ("Short", "Long", "A4", "PhotoPaper")
paper_type_combo.grid(row=1, column=3, padx=5, pady=5)
entries.append(paper_type_combo)

# Color (Dropdown)
color_var = tk.StringVar()
color_var.trace_add("write", validate_entries)
color_combo = ttk.Combobox(transaction_frame, width=10, textvariable=color_var, state="readonly")
color_combo['values'] = ("Black", "Colored")
color_combo.grid(row=1, column=4, padx=5, pady=5)
entries.append(color_combo)

# Pages (Integer only)
pages_var = tk.StringVar()
pages_var.trace_add("write", validate_entries)
pages_var.trace_add("write", suggest_total_price)
pages_entry = tk.Entry(transaction_frame, width=12, textvariable=pages_var, validate='key', validatecommand=vcmd_int)
pages_entry.grid(row=1, column=5, padx=5, pady=5)
entries.append(pages_entry)

# Price/Page (Float)
price_var = tk.StringVar()
price_var.trace_add("write", validate_entries)
price_var.trace_add("write", suggest_total_price)
price_entry = tk.Entry(transaction_frame, width=12, textvariable=price_var, validate='key', validatecommand=vcmd_float)
price_entry.grid(row=1, column=6, padx=5, pady=5)
entries.append(price_entry)

# Total (Float)
total_var = tk.StringVar()
total_var.trace_add("write", validate_entries)
total_entry = tk.Entry(transaction_frame, width=12, textvariable=total_var, validate='key', validatecommand=vcmd_float)
total_entry.grid(row=1, column=7, padx=5, pady=5)
entries.append(total_entry)

# Add Item Button
btn_additem = tk.Button(root, text="Add Item", width=10, bg="darkgreen", fg="white", state="disabled", command=add_item)
btn_additem.place(x=760, y=70) # Reverted to global root positioning

# Add Confirm Button
btn_confirm = tk.Button(root, text="Confirm Transaction", width=16, bg="steelblue", fg="white", command=confirm_transaction)
btn_confirm.place(x=860, y=250) # Reverted to global root positioning

# === Record Section ===
lbl_record = tk.Label(root, text="Record", font=("Arial", 16))
lbl_record.place(x=180, y=300)

record_frame = tk.Frame(root, bg="white", width=800, height=360, relief="solid", bd=1)
record_frame.place(x=180, y=330)

# Treeview for Record Table
columns = ("ID", "Date", "Time", "Paper Type", "Color", "Pages", "Price/Page", "Total")
record_table = ttk.Treeview(record_frame, columns=columns, show="headings", height=11)

for col in columns:
    record_table.heading(col, text=col)
    record_table.column(col, width=75, anchor="center")

record_table.grid(row=0, column=0, sticky="nsew")

# Scrollbar for Record Table
scrollbar = ttk.Scrollbar(record_frame, orient="vertical", command=record_table.yview)
record_table.configure(yscroll=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky="ns")

# Allow frame to expand properly
record_frame.grid_rowconfigure(0, weight=1)
record_frame.grid_columnconfigure(0, weight=1)

sales_summary_frame = tk.Frame(root, width=200, height=360, relief="solid", bd=0)
sales_summary_frame.place(x=810, y=350) # Reverted to global root positioning

lbl_summary_title = tk.Label(sales_summary_frame, text="Quick Sales Summary", font=("Arial", 12, "bold"))
lbl_summary_title.pack(pady=10)

# Today's Income
lbl_today_income = tk.Label(sales_summary_frame, text="Today's Income: ₱0.00", font=("Arial", 10))
lbl_today_income.pack(anchor="w", padx=10)

lbl_today_date = tk.Label(sales_summary_frame, text="", font=("Arial", 8, "italic"))
lbl_today_date.pack(anchor="w", padx=15)

# This Month
lbl_month_income = tk.Label(sales_summary_frame, text="This Month: ₱0.00", font=("Arial", 10))
lbl_month_income.pack(anchor="w", padx=10)

lbl_month_date = tk.Label(sales_summary_frame, text="", font=("Arial", 8, "italic"))
lbl_month_date.pack(anchor="w", padx=15)

# This Year
lbl_year_income = tk.Label(sales_summary_frame, text="This Year: ₱0.00", font=("Arial", 10))
lbl_year_income.pack(anchor="w", padx=10)

lbl_year_date = tk.Label(sales_summary_frame, text="", font=("Arial", 8, "italic"))
lbl_year_date.pack(anchor="w", padx=15)

# Bind right-click for records table
record_table.bind("<Button-3>", on_record_right_click)

record_menu = tk.Menu(root, tearoff=0)
record_menu.add_command(label="Edit Transaction", command=edit_selected_record)
record_menu.add_command(label="Delete Transaction", command=delete_selected_record)

# 📌 Load records from CSV after everything's initialized
load_records_from_csv(record_table)

# 📌 Update sales summary on initial load
update_sales_summary()

# Run main window
root.mainloop()