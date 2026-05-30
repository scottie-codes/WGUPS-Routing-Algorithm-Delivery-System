from constants import *
from models import Status
from utils import is_package_on_truck_at_time, package_status_at_time


def print_title():
    """
    Prints the program title.
    """
    print("\n")
    print("\n" + f"{BOLD}{CYAN}******* WGUPS PACKAGE DELIVERY SYSTEM *******{RESET}" + "\n")


def print_current_truck_status(trucks, drivers, time_check):
    """
    Prints the current status of each truck in a formatted table for UX consistency.

    Args:
        trucks (list): List of Truck objects.
        drivers (list): List of Driver objects.
        time_check (datetime): The time for which to report truck status.
    """
    from datetime import datetime
    import re

    print(f"\n{BOLD}{CYAN}All Truck Statuses at {time_check.strftime('%#I:%M %p')}{RESET}")
    print("=" * 99)
    print("| Truck   | Current Cargo on Truck                                         | Miles   | Driver     |")
    print("=" * 99)

    # Defines timing constraints
    delayed_ids = {6, 25, 28, 32}
    delayed_arrival_time = datetime.strptime("09:05", "%H:%M")
    package_9_correction_time = datetime.strptime("10:20", "%H:%M")

    for i, truck in enumerate(trucks):
        # Driver assignments
        if i == 0:
            driver = drivers[0]
        elif i == 1:
            driver = drivers[1]
        else:
            # For Truck 3, only assign driver if a driver has finished their route AND returned
            driver_assigned = False

            # see if Truck 1 has finished all deliveries and returned
            if (truck.departure_time and
                    len(trucks[0].packages) == 0 and  #
                    time_check >= trucks[0].current_time):
                driver = drivers[0]
                driver_assigned = True
            # check if Truck 2 has finished all deliveries and returned
            elif (truck.departure_time and
                  len(trucks[1].packages) == 0 and
                  time_check >= trucks[1].current_time):
                driver = drivers[1]
                driver_assigned = True

            # If both trucks are done assign one that finished first
            if (truck.departure_time and
                    len(trucks[0].packages) == 0 and len(trucks[1].packages) == 0 and
                    time_check >= max(trucks[0].current_time, trucks[1].current_time)):
                driver_name = drivers[0].name if trucks[0].current_time <= trucks[1].current_time else drivers[1].name
                driver = type('Driver', (), {'name': driver_name})()
                driver_assigned = True

            # If no driver is available yet
            if not driver_assigned:
                driver = type('Driver', (), {'name': 'Unassigned'})()

        # Filter packages actually on truck at this moment
        current_packages = []
        for p in truck.packages:
            # Skip if package is already delivered
            if p.delivery_time and time_check >= p.delivery_time:
                continue

            # Skip if truck hasn't departed yet ( still at hub)
            if truck.departure_time and time_check < truck.departure_time:                continue

            # Skip delayed packages if they haven't arrived yet
            if p.package_id in delayed_ids and time_check < delayed_arrival_time:
                continue

            # Skip Package 9 if address not corrected yet
            if p.package_id == 9 and time_check < package_9_correction_time:
                continue

            # If we get here, package is currently on the truck
            current_packages.append(p)

        # Determine what to show in cargo column
        if len(truck.packages) == 0 and truck.departure_time and time_check >= truck.current_time:
            # Truck has departed and finished all deliveries
            cargo_display = f"{GREEN}All Packages Delivered{RESET}"
        elif current_packages:
            # Show current package IDs in yellow
            package_ids = [f"{YELLOW}{p.package_id}{RESET}" for p in current_packages]
            cargo_display = ', '.join(package_ids)
        else:
            # else show nothing
            cargo_display = ""

        # Strip ANSI color codes so table columns line up correctly, was messing up formatting
        display_length = len(re.sub(r'\x1b\[[0-9;]*m', '', cargo_display))

        # pad to 63 characters for cargo column
        padding_needed = 63 - display_length
        cargo_display = cargo_display + (' ' * padding_needed)

        print(
            f"| {'Truck ' + str(i + 1):<7}"
            f"| {cargo_display} "
            f"| {f'{truck.miles:.2f}':<7} "
            f"| {driver.name[:10].ljust(10)} |"
        )

    print("=" * 99)

    # Calculates total mileage for interface
    total_miles = sum(truck.miles for truck in trucks)

    # Prints total mileage row with formatting
    print(f"{' ' * 61}{BOLD}Total Mileage | {BOLD}{GREEN}{f'{total_miles:.2f}':<7}{RESET} |")
    print(f"{' ' * 75}{'=' * 11}")


def print_package_status_summary_table(package_hash, t1_pkgs, t2_pkgs, t3_pkgs, time_check):
    """
    Prints a summary table of all package statuses at a specific time (with clean custom CLI formatting for better UX).

    Args:
        package_hash (DynamicHashTable): Hash table of all packages.
        t1_pkgs, t2_pkgs, t3_pkgs (list): Lists of packages on each truck.
        time_check (datetime): The time to report statuses.
    """
    delivered, attempted, errors = 0, 0, []
    # Loop through all possible IDs
    for pkg_id in range(1, 41):
        pkg = package_hash.search(pkg_id)
        if pkg:
            attempted += 1
            # tally delivered and invalid counts
            if package_status_at_time(pkg, time_check) == Status.DELIVERED.value:
                delivered += 1
            if package_status_at_time(pkg, time_check) == Status.INVALID.value:
                errors.append(
                    f"Package {pkg.package_id} could not be delivered due to address issue: \"{pkg.notes}\""
                )
    print(f"{CYAN}Packages Delivered: {GREEN}{delivered}{RESET} out of {attempted}{RESET}")
    if errors:
        print(f"{RED}Delivery Errors:{RESET}")
        for e in errors:
            print(f"  {RED}- {e}{RESET}")

    # clean, custom formatting for package output
    print()
    print(f"{BOLD}{CYAN}All Package Delivery Statuses at {time_check.strftime('%#I:%M %p')}{RESET}")
    print("===================================================================================================")
    print("| ID  | Address                   | Deadline  | Status           | Delivery Time | Assigned Truck |")
    print("===================================================================================================")
    for pkg_id in range(1, 41):
        pkg = package_hash.search(pkg_id)
        if pkg:
            delivery_time_str = pkg.delivery_time.strftime("%#I:%M %p") if pkg.delivery_time else "None"
            addr = pkg.address[:25].ljust(25)
            stat = package_status_at_time(pkg, time_check).ljust(16)
            current_status = package_status_at_time(pkg, time_check)

            # if delivered after deadline and not EOD, late package
            late = False
            if (
                    pkg.delivery_time
                    and pkg.deadline != "EOD"
            ):
                try:
                    deadline_time = datetime.strptime(pkg.deadline, "%I:%M %p")
                    actual_delivery = pkg.delivery_time.replace(second=0, microsecond=0)
                    deadline_datetime = pkg.delivery_time.replace(
                        hour=deadline_time.hour, minute=deadline_time.minute, second=0, microsecond=0
                    )
                    if actual_delivery > deadline_datetime:
                        late = True
                except Exception:
                    late = False

            # make delivery time red IF package is late so I can see if I'm meeting deadlines
            delivery_time_print = (
                f"{RED}{delivery_time_str}{RESET}".ljust(13 + len(RED) + len(RESET))
                if late else delivery_time_str.ljust(13)
            )

            if current_status == Status.DELIVERED.value:
                color = GREEN
            elif current_status in (Status.INVALID.value, Status.DELAYED.value):
                color = RED
            else:
                color = YELLOW

            if pkg in t1_pkgs:
                truck_str = "Truck 1"
            elif pkg in t2_pkgs:
                truck_str = "Truck 2"
            elif pkg in t3_pkgs:
                truck_str = "Truck 3"
            else:
                truck_str = "Not loaded yet"

            print(f"| {str(pkg.package_id).ljust(3)} | {addr} | {pkg.deadline.ljust(9)} | "
                  f"{color}{stat}{RESET} | {delivery_time_print} | {truck_str.ljust(15)}|")

    print("===================================================================================================")
    # Show which packages are currently loaded on each truck


def print_total_mileage(trucks):
    """
    Prints the total mileage traveled by all trucks.

    Args:
        trucks (list): List of Truck objects.
    """

    total_miles = sum(truck.miles for truck in trucks)
    print(f"{WHITE_BOLD}Total mileage for all trucks:{RESET} {GREEN}{total_miles:.2f} miles{RESET}\n")


def print_mileage_and_driver_report(trucks, drivers):
    """
    Prints detailed mileage and trip reports for each truck and driver.

    Args:
        trucks (list): List of Truck objects.
        drivers (list): List of Driver objects.
    """

    print_total_mileage(trucks)
    print(f"{WHITE_BOLD}Mileage Breakdown:{RESET}")
    # assigns Driver A to Truck 1 and B to Truck 2
    # Whichever driver gets back first drives the 3rd truck for their second run
    for i, truck in enumerate(trucks, 1):
        if i == 1:
            driver = drivers[0]
        elif i == 2:
            driver = drivers[1]
        else:
            driver = drivers[0] if trucks[0].current_time <= trucks[1].current_time else drivers[1]
        print(f"  {BOLD}Truck {i}:{RESET} {GREEN}{truck.miles:.2f} miles{RESET} ({driver.name})")
    print()
    # print stats for driver report with formatting
    for driver in drivers:
        print(f"{WHITE_BOLD}{driver.name} - Total Miles Driven: {GREEN}{driver.total_miles:.2f}{RESET}")
        print(f"  Trip History:")
        if driver.truck_history:
            for trip in driver.truck_history:
                truck_id, miles, start, end = trip
                # Convert to 12 hours format for better UX
                start_12hr = datetime.strptime(start, "%H:%M:%S").strftime("%#I:%M %p")
                end_12hr = datetime.strptime(end, "%H:%M:%S").strftime("%I:%M %p")
                print(f"     {BOLD}{truck_id}: {miles:.2f} miles | Start Time: {start_12hr} | End Time: {end_12hr}")
        else:
            print("    (No runs completed)")
        print()
