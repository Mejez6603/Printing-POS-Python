import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from sales_report import filter_records_by_date, export_report_as_csv
import os
from tkinter import filedialog

def open_sales_report_window(root):
    report_window = tk.Toplevel(root)
    report_window.title("Sales Report")
    # Slightly increased height to accommodate new summary lines
    report_window.geometry("500x520") # Retained this geometry as it fits the content well
    report_window.resizable(False, False)

    # Make grid columns and rows expandable (important for Treeview)
    report_window.grid_columnconfigure(0, weight=1)
    report_window.grid_columnconfigure(1, weight=1)
    report_window.grid_columnconfigure(2, weight=1)
    report_window.grid_columnconfigure(3, weight=1)
    report_window.grid_columnconfigure(4, weight=1)
    report_window.grid_rowconfigure(3, weight=1) # Row for the Treeview

    # --- Title ---
    title_label = tk.Label(report_window, text="Sales Report", font=("Arial", 15, "bold"))
    title_label.grid(row=0, column=0, columnspan=5, pady=(8, 12))

    # --- Date Range Selection Frame ---
    date_selection_frame = tk.Frame(report_window)
    date_selection_frame.grid(row=1, column=0, columnspan=5, pady=0)

    date_from_label = tk.Label(date_selection_frame, text="Date From:")
    date_from_label.pack(side="left", padx=(20, 2))

    date_from_entry = tk.Entry(date_selection_frame, width=12)
    date_from_entry.pack(side="left", padx=(0, 2))
    date_from_entry.insert(0, datetime.now().strftime("%m/%d/%Y"))

    date_to_label = tk.Label(date_selection_frame, text="-")
    date_to_label.pack(side="left", padx=(2, 2))

    date_to_entry = tk.Entry(date_selection_frame, width=12)
    date_to_entry.pack(side="left", padx=(0, 5))
    date_to_entry.insert(0, datetime.now().strftime("%m/%d/%Y"))

    def generate_report():
        from_date_str = date_from_entry.get()
        to_date_str = date_to_entry.get()
        try:
            from_dt = datetime.strptime(from_date_str, "%m/%d/%Y")
            to_dt = datetime.strptime(to_date_str, "%m/%d/%Y")
            if from_dt > to_dt:
                messagebox.showerror("Invalid Date Range", "Date From cannot be after Date To.")
                return
        except ValueError:
            messagebox.showerror("Invalid Date Format", "Please use MM/DD/YYYY format for dates.")
            return

        headers, records = filter_records_by_date(from_date_str, to_date_str)
        populate_report_tree(headers, records)
        update_summary(records)

    generate_button = tk.Button(date_selection_frame, text="Generate Report", command=generate_report)
    generate_button.pack(side="left", padx=(5, 0))

    # --- Quick Date Range Buttons Frame ---
    quick_buttons_frame = tk.Frame(report_window)
    quick_buttons_frame.grid(row=2, column=0, columnspan=5, pady=(10, 15))

    def set_date_range(start_date, end_date):
        date_from_entry.delete(0, tk.END)
        date_from_entry.insert(0, start_date.strftime("%m/%d/%Y"))
        date_to_entry.delete(0, tk.END)
        date_to_entry.insert(0, end_date.strftime("%m/%d/%Y"))
        generate_report()

    today_button = tk.Button(quick_buttons_frame, text="Today",
                             bg="steelblue", fg="white",
                             command=lambda: set_date_range(datetime.now(), datetime.now()))
    today_button.pack(side="left", padx=(20, 2), expand=True, fill="x")

    now = datetime.now()
    start_of_week = now - timedelta(days=now.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    this_week_button = tk.Button(quick_buttons_frame, text="This Week",
                                  bg="steelblue", fg="white",
                                  command=lambda: set_date_range(start_of_week, end_of_week))
    this_week_button.pack(side="left", padx=2, expand=True, fill="x")

    start_of_month = now.replace(day=1)
    next_month = start_of_month.replace(day=28) + timedelta(days=4)
    end_of_month = next_month - timedelta(days=next_month.day)
    this_month_button = tk.Button(quick_buttons_frame, text="This Month",
                                   bg="steelblue", fg="white",
                                   command=lambda: set_date_range(start_of_month, end_of_month))
    this_month_button.pack(side="left", padx=2, expand=True, fill="x")

    start_of_year = now.replace(month=1, day=1)
    end_of_year = now.replace(month=12, day=31)
    this_year_button = tk.Button(quick_buttons_frame, text="This Year",
                                  bg="steelblue", fg="white",
                                  command=lambda: set_date_range(start_of_year, end_of_year))
    this_year_button.pack(side="left", padx=(2, 20), expand=True, fill="x")

    # --- Report Treeview ---
    report_frame = tk.Frame(report_window)
    report_frame.grid(row=3, column=0, columnspan=5, padx=10, pady=(5, 5), sticky="nsew")

    report_columns = ("ID", "Date", "Time", "Paper Type", "Color", "Pages", "Price/Page")
    report_tree = ttk.Treeview(report_frame, columns=report_columns, show="headings")

    report_tree.heading("ID", text="ID")
    report_tree.column("ID", width=60, anchor="center")
    report_tree.heading("Date", text="Date")
    report_tree.column("Date", width=65, anchor="center")
    report_tree.heading("Time", text="Time")
    report_tree.column("Time", width=60, anchor="center")
    report_tree.heading("Paper Type", text="Paper Type")
    report_tree.column("Paper Type", width=75, anchor="center")
    report_tree.heading("Color", text="Color")
    report_tree.column("Color", width=60, anchor="center")
    report_tree.heading("Pages", text="Pages")
    report_tree.column("Pages", width=50, anchor="center")
    report_tree.heading("Price/Page", text="Price/Page")
    report_tree.column("Price/Page", width=70, anchor="center")

    report_tree.pack(side="left", fill="both", expand=True)

    report_scrollbar = ttk.Scrollbar(report_frame, orient="vertical", command=report_tree.yview)
    report_tree.configure(yscrollcommand=report_scrollbar.set)
    report_scrollbar.pack(side="right", fill="y")

    def populate_report_tree(headers, records):
        for item in report_tree.get_children():
            report_tree.delete(item)
        for record in records:
            display_values = list(record[:7])
            try:
                price_per_page = float(display_values[6])
                display_values[6] = f"₱{price_per_page:,.2f}"
            except (ValueError, IndexError):
                pass
            report_tree.insert("", "end", values=display_values)

    # --- Summary Statistics Frame ---
    summary_and_export_frame = tk.Frame(report_window)
    summary_and_export_frame.grid(row=4, column=0, columnspan=5, padx=10, pady=(8, 10), sticky="ew")
    summary_and_export_frame.grid_columnconfigure(0, weight=1) # For summary labels
    summary_and_export_frame.grid_columnconfigure(1, weight=1) # For export buttons

    # Summary Labels (left side) - Now using grid for horizontal layout
    summary_labels_frame = tk.Frame(summary_and_export_frame)
    summary_labels_frame.grid(row=0, column=0, sticky="w")
    # Configure grid columns for summary labels for even distribution
    summary_labels_frame.grid_columnconfigure(0, weight=1)
    summary_labels_frame.grid_columnconfigure(1, weight=1)
    summary_labels_frame.grid_columnconfigure(2, weight=1)


    # Row 0
    total_sales_label = tk.Label(summary_labels_frame, text="Total Sales: ₱0.00", font=("Arial", 8, "bold"))
    total_sales_label.grid(row=0, column=0, sticky="w", padx=2, pady=1)

    lbl_total_short_pages = tk.Label(summary_labels_frame, text="Total Short Pages: 0", font=("Arial", 8))
    lbl_total_short_pages.grid(row=0, column=1, sticky="w", padx=2, pady=1)

    lbl_total_black_pages = tk.Label(summary_labels_frame, text="Total Black Pages: 0", font=("Arial", 8))
    lbl_total_black_pages.grid(row=0, column=2, sticky="w", padx=2, pady=1)

    # Row 1
    total_pages_label = tk.Label(summary_labels_frame, text="Total Pages: 0", font=("Arial", 8))
    total_pages_label.grid(row=1, column=0, sticky="w", padx=2, pady=1)

    lbl_total_long_pages = tk.Label(summary_labels_frame, text="Total Long Pages: 0", font=("Arial", 8))
    lbl_total_long_pages.grid(row=1, column=1, sticky="w", padx=2, pady=1)

    lbl_total_colored_pages = tk.Label(summary_labels_frame, text="Total Colored Pages: 0", font=("Arial", 8))
    lbl_total_colored_pages.grid(row=1, column=2, sticky="w", padx=2, pady=1)

    # Row 2
    transactions_label = tk.Label(summary_labels_frame, text="Transactions: 0", font=("Arial", 8))
    transactions_label.grid(row=2, column=0, sticky="w", padx=2, pady=1)

    lbl_total_a4_pages = tk.Label(summary_labels_frame, text="Total A4 Pages: 0", font=("Arial", 8))
    lbl_total_a4_pages.grid(row=2, column=1, sticky="w", padx=2, pady=1)

    # NEW: Total PhotoPaper Pages
    lbl_total_photopaper_pages = tk.Label(summary_labels_frame, text="Total PhotoPaper Pages: 0", font=("Arial", 8))
    lbl_total_photopaper_pages.grid(row=2, column=2, sticky="w", padx=2, pady=1)  # Placed in row 2, column 2

    # No label for row 2, column 2 in this layout for now


    def update_summary(records):
        total_sales = 0.0
        total_pages = 0
        unique_transaction_ids = set()
        total_short_pages = 0
        total_long_pages = 0
        total_a4_pages = 0
        total_black_pages = 0
        total_colored_pages = 0
        total_photopaper_pages = 0

        for record in records:
            try:
                total_sales += float(record[7]) # Index 7 for Total
            except (ValueError, IndexError):
                pass

            try:
                pages = int(record[5]) # Index 5 for Pages
                total_pages += pages

                paper_type = record[3].lower() # Index 3 for Paper Type
                if paper_type == "short":
                    total_short_pages += pages
                elif paper_type == "long":
                    total_long_pages += pages
                elif paper_type == "a4":
                    total_a4_pages += pages
                elif paper_type == "photopaper":
                    total_photopaper_pages += pages

                color_type = record[4].lower() # Index 4 for Color
                if color_type == "black":
                    total_black_pages += pages
                elif color_type == "colored":
                    total_colored_pages += pages

            except (ValueError, IndexError):
                pass

            try:
                unique_transaction_ids.add(record[0]) # Index 0 for ID
            except IndexError:
                pass

        total_sales_label.config(text=f"Total Sales: ₱{total_sales:,.2f}")
        total_pages_label.config(text=f"Total Pages: {total_pages}")
        transactions_label.config(text=f"Transactions: {len(unique_transaction_ids)}")

        lbl_total_short_pages.config(text=f"Total Short Pages: {total_short_pages}")
        lbl_total_long_pages.config(text=f"Total Long Pages: {total_long_pages}")
        lbl_total_a4_pages.config(text=f"Total A4 Pages: {total_a4_pages}")
        lbl_total_black_pages.config(text=f"Total Black Pages: {total_black_pages}")
        lbl_total_colored_pages.config(text=f"Total Colored Pages: {total_colored_pages}")
        lbl_total_photopaper_pages.config(text=f"Total PhotoPaper Pages: {total_photopaper_pages}")

    # Export Buttons (right side)
    export_buttons_frame = tk.Frame(summary_and_export_frame)
    export_buttons_frame.grid(row=0, column=1, sticky="ne")

    def export_to_csv():
        from_date_str = date_from_entry.get()
        to_date_str = date_to_entry.get()
        headers, data_to_export = filter_records_by_date(from_date_str, to_date_str)

        if not data_to_export:
            messagebox.showinfo("No Data", "No data to export.")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                                initialdir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports"),
                                                initialfile=f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        if filepath:
            export_report_as_csv([headers] + data_to_export, filepath)
            messagebox.showinfo("Export Successful", f"Report exported to {filepath}")

    export_csv_button = tk.Button(export_buttons_frame, text="Export as CSV", command=export_to_csv)
    export_csv_button.pack(pady=0, padx=(0, 10), anchor="e")

    def export_to_pdf():
        messagebox.showinfo("Not Implemented", "Export to PDF functionality is not yet implemented.")

    export_pdf_button = tk.Button(export_buttons_frame, text="Export as PDF", command=export_to_pdf)
    export_pdf_button.pack(pady=0, padx=(0, 10), anchor="e")

    # Initial report generation for today's date
    set_date_range(datetime.now(), datetime.now())

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Test Sales Report Window")
    open_sales_report_window(root)
    root.mainloop()