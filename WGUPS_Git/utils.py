import re
import csv
import os
from datetime import datetime

from constants import START_TIME, CYAN, RED, RESET  # For color and start time constants
from models import Package, Status



def normalize_address(address):
    """


    Normalizes a delivery address string for comparisons.

     Args:
         address (str): The raw address to normalize.

     Returns:
         str: The cleaned, lowercased address.
     """
    # Tried to give general normalizing rules in case different data is ever used
    address = address.split('\n')[-1] #Only takes last line if multiple lines
    address = re.sub(r'\([^)]*\)', '', address) #removes anything in parentheses
    address = address.replace(',', ' ') # Replace commas with spaces
    address = re.sub(r'\s+', ' ', address) # Removes extra spaces
    return address.strip().lower() # strips whitespace and makes it lowercase for easy comparisons


def load_distance_matrix_data(file_path):
    """
     Loads address and distance data from a CSV distance table file.

     Args:
         file_path (str): Path to the CSV file.

     Returns:
         tuple: (list of addresses, 2D list of distances)
     """
    distance_matrix, address_list = [], []
    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        # finds header row (csv files were messy)
        while True:
            header_row = next(csv_reader)
            if header_row and header_row[0].lower().startswith("location name"):
                break
        address_list = [normalize_address(addr) for addr in header_row[2:]]
        for row in csv_reader:
            if not row or not row[1].strip():
                continue
            # Convert distance string cells to float and if empty to 0.0 float
            row_distances = [float(cell.strip()) if cell.strip() else 0.0 for cell in row[2:]]
            distance_matrix.append(row_distances)
    return address_list, distance_matrix


def get_distance(i, j, matrix):
    """
    Returns the distance between two addresses by index.

    Args:
        i (int): Index of first address.
        j (int): Index of second address.
        matrix (list): 2D distance matrix provided by WGU as CSV in task requirement section.

    Returns:
        float: The distance between address i and j.
    """
    # Still will work if WGUPS changes their matrix to upper or it isn't equal
    return matrix[i][j] if i > j else matrix[j][i]


def load_package_data(file_path, hash_table):
    """
      Loads all package data from a CSV file and inserts it into the hash table.

      Args:
          file_path (str): Path to the package CSV file.
          hash_table (DynamicHashTable): The table to insert packages into.
      """
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for row in csv_reader:
            if not row or row[0].strip() == "":
                continue
            try:
                # Parses all package fields, handles any extra columns as note fields
                pkg = Package(
                    int(row[0]), row[1].strip(), row[2].strip(), row[3].strip(),
                    int(row[4].strip()), row[5].strip(), float(row[6].strip()),
                    ', '.join(cell.strip() for cell in row[7:] if cell.strip()))
                hash_table.insert(pkg.package_id, pkg)
            except:
                # skips poorly formatted rows
                continue


def get_time_from_user():
    """
    Prompts the user for a time input and returns a datetime object.

    Returns:
        datetime: User-entered time.
    """
    while True:
        t = input(f"{CYAN}Enter a time in 24hr or 12hr + am/pm format (HH:MM, or H:MM and am/pm): {RESET}").strip()
        # try different time formats to make it easy for user
        for fmt in ("%H:%M", "%I:%M%p", "%I:%M %p"):
            try:
                d = datetime.strptime(t, fmt)
                # Return today's date with the selected time (chose not to use seconds for better UX)
                return START_TIME.replace(hour=d.hour, minute=d.minute)
            except Exception:
                continue
        print(f"{RED}INVALID TIME FORMAT. Try a format like 08:30 or 1:00pm.{RESET}")


def is_package_on_truck_at_time(pkg, time_check):
    """
    Determines if a package is currently on the truck at a specific time.

    Args:
        pkg (Package): The package to check.
        time_check (datetime): The time to check.

    Returns:
        bool: True if package is still on truck at this time.
    """

    # If left hub time is none, still at hub
    if pkg.left_hub_time is None:
        return True
    # If package has delivery time, NOT on truck
    if pkg.delivery_time is not None and time_check >= pkg.delivery_time:
        return False
    # If current time is before left hub, NOT on truck
    if time_check < pkg.left_hub_time:
        return False
    # If time is between when it leaves hub and when it is delivered, on truck
    if (pkg.left_hub_time is not None and
            (pkg.delivery_time is None or time_check < pkg.delivery_time) and
            time_check >= pkg.left_hub_time):
        return True
    return False


def package_status_at_time(pkg, time_check):
    """
    Returns the *dynamic* status of a package at a given time,
    including all logic for delays, invalid addresses, and delivery.
    """


    delayed_ids = {6, 25, 28, 32}
    delayed_until = datetime.strptime("09:05", "%H:%M")

    # Usual logic for other packages and for package 9 after address correction
    if pkg.status == Status.INVALID:
        return Status.INVALID.value
    if pkg.package_id in delayed_ids and time_check < delayed_until:
        return Status.DELAYED.value
    if pkg.delivery_time and time_check >= pkg.delivery_time:
        return Status.DELIVERED.value
    elif pkg.left_hub_time and time_check >= pkg.left_hub_time:
        return Status.EN_ROUTE.value
    return Status.AT_HUB.value



def clear_screen():
    """
    Clears the terminal/console screen for better CLI appearance.
    """
    # Works for both Windows and Unix/ Mac to clear the console for cleaner readability / UX
    os.system('cls' if os.name == 'nt' else 'clear')
