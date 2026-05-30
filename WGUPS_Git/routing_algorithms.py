from utils import normalize_address, get_distance
from models import Truck
from constants import TRUCK_CAPACITY
from models import Status
from datetime import datetime, timedelta

def deadline_priority(deadline_str):
    """
    Converts deadline to priority number for sorting (lower = more urgent)
    """
    if deadline_str == "EOD":
        return float('inf')  # I use infinity for lowest priority
    else:
        # Convert time to minutes from midnight for comparison
        deadline_time = datetime.strptime(deadline_str, "%I:%M %p")
        return deadline_time.hour * 60 + deadline_time.minute


def nearest_neighbor_algorithm(truck, distance_matrix, address_list, cutoff_time):
    """
    Uses the Nearest Neighbor Algorithm to determine the best delivery route for a truck.

    Args:
        truck (Truck): The truck object containing packages.
        distance_matrix (list): 2D list of distances between addresses.
        address_list (list): List of addresses.
        cutoff_time (datetime): The time to stop simulating deliveries.
    """
    visited = set()
    current_index = 0

    # Mark hub departure time for each package on truck
    for pkg in truck.packages:
        pkg.left_hub_time = truck.departure_time

    delayed_ids = {6, 25, 28, 32}
    delayed_time = datetime.strptime("09:05", "%H:%M")

    while truck.packages:
        # if truck's current time is >= cutoff, stop sim
        if truck.current_time >= cutoff_time:
            break

        nearest_package, nearest_distance, nearest_index = None, float('inf'), None

        eligible_packages = []

        for package in truck.packages:
            # skip delayed packages
            if package.package_id in delayed_ids and truck.current_time < delayed_time:
                continue

            # if address isn't corrected yet, skip package 9
            address_correction_time = datetime.strptime("10:20", "%H:%M")
            if package.package_id == 9 and truck.current_time < address_correction_time:
                continue

            # normalize package and address logic
            package_addr_norm = normalize_address(package.address)
            delivery_index = next((i for i, addr in enumerate(address_list) if package_addr_norm == addr), None)
            if delivery_index is None or delivery_index in visited:
                continue

            d = get_distance(current_index, delivery_index, distance_matrix)

            # Collect all deliverable packages with their distance and deadline priority
            eligible_packages.append((package, d, delivery_index, deadline_priority(package.deadline)))

        if eligible_packages:
            # Sort by deadline first, then by distance
            eligible_packages.sort(key=lambda x: (x[3], x[1], x[0].package_id))
            nearest_package, nearest_distance, nearest_index, _ = eligible_packages[0]
        else:
            nearest_package = None

        if nearest_package:
            # stop if delivery of this package will finish after cutoff_time
            travel_time = timedelta(hours=(nearest_distance / truck.speed))
            arrival_time = truck.current_time + travel_time

            if arrival_time > cutoff_time:
                break  # Do not deliver, simulation ends here

            # Deliver nearest package
            truck.package_delivery(nearest_package, nearest_distance, nearest_index)
            visited.add(nearest_index)
            current_index = nearest_index

            # deliver any package with same address together
            for pkg2 in list(truck.packages):
                if (normalize_address(pkg2.address) == normalize_address(nearest_package.address)
                        and pkg2.package_id != nearest_package.package_id
                        and "wrong address listed" not in pkg2.notes.lower()):
                    pkg2.status = Status.DELIVERED
                    pkg2.delivery_time = truck.current_time
                    pkg2.left_hub_time = pkg2.left_hub_time or truck.departure_time
                    truck.packages.remove(pkg2)
            truck.packages.remove(nearest_package)
        else:

            break


def assign_packages_to_trucks(all_packages):
    """
    Assigns packages to trucks based on constraints and package notes.
    Meets deadlines by putting urgent packages on morning trucks.

    Args:
        all_packages (list): List of all Package objects.

    Returns:
        tuple: (truck1_packages, truck2_packages, truck3_packages)
    """
    t1, t2, t3, assigned = [], [], [], set()  # Lists for each truck and sets to track IDs

    # handle important constraints first
    for pkg in all_packages:
        if not pkg or pkg.package_id in assigned:
            continue

        note = pkg.notes.lower().strip()

        # if must be delivered together, assign to Truck 1
        if pkg.package_id in {13, 14, 15, 16, 19, 20}:
            t1.append(pkg)
            assigned.add(pkg.package_id)
        # has to be on truck 2
        elif "can only be on truck 2" in note:
            t2.append(pkg)
            assigned.add(pkg.package_id)
        # Only packages that are delayed go to Truck 3
        elif "delayed on flight" in note or "wrong address listed" in note:
            t3.append(pkg)
            assigned.add(pkg.package_id)

    # Assign remaining packages while prioritizing urgent deadlines on early trucks
    urgent_packages = []
    eod_packages = []

    for pkg in all_packages:
        if not pkg or pkg.package_id in assigned:
            continue

        if pkg.deadline != "EOD":
            urgent_packages.append(pkg)
        else:
            eod_packages.append(pkg)

    # sort urgent packages by deadline (earliest get priority)
    urgent_packages.sort(key=lambda p: datetime.strptime(p.deadline, "%I:%M %p"))

    # Assign urgent packages to Trucks 1 and 2 first, they leave at 8am
    for pkg in urgent_packages:
        if len(t1) < TRUCK_CAPACITY:
            t1.append(pkg)
        elif len(t2) < TRUCK_CAPACITY:
            t2.append(pkg)
        else:
            # if no room, last resort- urgent package goes to late truck
            t3.append(pkg)
        assigned.add(pkg.package_id)

    # Assign EOD packages to fill remaining space
    for pkg in eod_packages:
        if len(t1) < TRUCK_CAPACITY:
            t1.append(pkg)
        elif len(t2) < TRUCK_CAPACITY:
            t2.append(pkg)
        else:
            t3.append(pkg)
        assigned.add(pkg.package_id)

    return t1, t2, t3
