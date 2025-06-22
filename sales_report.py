import os, csv
from datetime import datetime

# Path to records.csv inside /database/
# IMPORTANT CHANGE: Make the DATABASE_PATH resolution robust for bundled applications
base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
DATABASE_PATH = os.path.join(base_dir, "database", "records.csv")  # Build the path relative to the script


def generate_daily_sales_report(date):
    """Calculate total sales for a specific date (MM/DD/YYYY)"""
    total = 0
    if not os.path.exists(DATABASE_PATH):
        # If the file doesn't exist, it means no data or path is wrong
        # For debugging, you could add: print(f"DEBUG: Data file not found at {DATABASE_PATH}")
        return total

    with open(DATABASE_PATH, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        try:
            next(reader)  # skip header
        except StopIteration:
            return total  # File is empty, no data rows
        for row in reader:
            if row[1] == date:  # 2nd column is Date
                try:
                    total += float(row[7])  # 8th column is Total
                except (ValueError, IndexError):
                    # Handle cases where Total might be malformed or row too short
                    continue
    return total


def generate_monthly_sales_report(month_year):
    """Calculate total sales for a specific month (MM/YYYY)"""
    total = 0
    if not os.path.exists(DATABASE_PATH):
        return total

    with open(DATABASE_PATH, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        try:
            next(reader)
        except StopIteration:
            return total  # File is empty
        for row in reader:
            try:
                row_date = datetime.strptime(row[1], "%m/%d/%Y")
                row_month_year = row_date.strftime("%m/%Y")
                if row_month_year == month_year:
                    total += float(row[7])
            except (ValueError, IndexError):
                # Handle cases where Date or Total might be malformed or row too short
                continue
    return total


def filter_records_by_date(from_date, to_date):
    """Get all records between two dates (MM/DD/YYYY)"""
    records = []
    if not os.path.exists(DATABASE_PATH):
        return [], []  # Return headers and empty records

    from_dt = datetime.strptime(from_date, "%m/%d/%Y")
    to_dt = datetime.strptime(to_date, "%m/%d/%Y")

    with open(DATABASE_PATH, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        headers = []
        try:
            headers = next(reader)  # Get headers
        except StopIteration:
            return [], []  # File is empty, no headers or data

        for row in reader:
            try:
                row_date = datetime.strptime(row[1], "%m/%d/%Y")
                if from_dt <= row_date <= to_dt:
                    records.append(row)
            except (ValueError, IndexError):
                # Handle cases where Date might be malformed or row too short
                continue

    return headers, records


def export_report_as_csv(report_data, filename):
    """Export a given report data into a CSV file"""
    # For exporting, ensure the 'reports' directory exists relative to the main app execution
    reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    export_file_path = os.path.join(reports_dir, filename)

    with open(export_file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for row in report_data:
            writer.writerow(row)