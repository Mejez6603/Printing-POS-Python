import os
import csv

# Get the directory where the main executable (or script) is running from.
# When PyInstaller creates a --onedir bundle, this __file__ path correctly
# points to the executable's directory within the bundle.
base_dir = os.path.dirname(os.path.abspath(__file__))
database_dir = os.path.join(base_dir, "database")
file_path = os.path.join(database_dir, "records.csv")

def save_records_to_csv(record_table):
    if not os.path.exists(database_dir):
        os.makedirs(database_dir)

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Ensure header is written even if table is empty (for fresh start)
        writer.writerow([record_table.heading(col)["text"] for col in record_table["columns"]])
        for child in record_table.get_children():
            writer.writerow(record_table.item(child)["values"])

def load_records_from_csv(record_table):
    if os.path.exists(file_path):
        with open(file_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            try:
                next(reader) # Skip header row
            except StopIteration:
                # File is empty or only has a header, which is fine
                pass
            for row in reader:
                record_table.insert("", 0, values=row)
    else:
        # If records.csv doesn't exist, create it with just headers.
        # This handles the very first run of the portable app.
        print(f"No records.csv found at {file_path}. Creating new file with headers.")
        if not os.path.exists(database_dir):
            os.makedirs(database_dir)
        headers = ["ID", "Date", "Time", "Paper Type", "Color", "Pages", "Price/Page", "Total"]
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)


def validate_integer(P):
    return P.isdigit() or P == ""

def validate_float(P):
    if P == "":
        return True
    try:
        float(P)
        return True
    except ValueError:
        return False