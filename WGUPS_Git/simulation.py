from constants import START_TIME
from hash_table import DynamicHashTable
from models import Driver, Truck
from routing_algorithms import nearest_neighbor_algorithm, assign_packages_to_trucks
from utils import load_distance_matrix_data, load_package_data
from datetime import datetime

def simulate_to_time(query_time):
    """
    Runs the simulation up to a specific time (query_time).

    Args:
        query_time (datetime): The time to simulate up to.

    Returns:
        (package_hash, t1_pkgs, t2_pkgs, t3_pkgs, trucks, driver_a, driver_b):
            - package_hash: hash table of all packages with states as of 'query_time'
            - t1_pkgs, t2_pkgs, t3_pkgs: packages on each truck (initial assignments)
            - trucks: list of Truck objects as of 'query_time'
            - driver_a, driver_b: Driver objects as of 'query_time'
    """

    # Reset All Data
    package_hash = DynamicHashTable()
    load_package_data("WGUPS_Package_Data", package_hash)
    addresses, distances = load_distance_matrix_data("WGUPS_Distance_Table")

    driver_a = Driver("Driver A")
    driver_b = Driver("Driver B")
    truck1 = Truck("Truck 1", START_TIME)
    truck2 = Truck("Truck 2", START_TIME)
    truck3 = Truck("Truck 3", None)

    all_packages = [package_hash.search(i) for i in range(1, 41)]
    t1_pkgs, t2_pkgs, t3_pkgs = assign_packages_to_trucks(all_packages)
    truck1.packages, truck2.packages = t1_pkgs[:], t2_pkgs[:]
    truck3.packages = []  # Truck 3 is empty until a driver is available

    #simulate deliveries until the query time

    # Truck 1
    nearest_neighbor_algorithm(truck1, distances, addresses, query_time)
    driver_a.drive(truck1, truck1.departure_time, min(truck1.current_time, query_time))

    # Truck 2
    nearest_neighbor_algorithm(truck2, distances, addresses, query_time)
    driver_b.drive(truck2, truck2.departure_time, min(truck2.current_time, query_time))

    # Truck 3. Only depart when a driver is back
    # calculate truck completion time
    temp_truck1 = Truck("Temp1", START_TIME)
    temp_truck2 = Truck("Temp2", START_TIME)
    temp_truck1.packages = t1_pkgs[:]
    temp_truck2.packages = t2_pkgs[:]

    # Run trucks to end of day (to solve early finish problem I was having)
    nearest_neighbor_algorithm(temp_truck1, distances, addresses, datetime.strptime("23:59", "%H:%M"))
    nearest_neighbor_algorithm(temp_truck2, distances, addresses, datetime.strptime("23:59", "%H:%M"))

    # Now we know actual truck finish time
    first_back_time = min(temp_truck1.current_time, temp_truck2.current_time)

    if query_time > first_back_time:
        # Now load truck 3
        afternoon_driver = driver_a if truck1.current_time <= truck2.current_time else driver_b
        truck3.reset(first_back_time)
        truck3.packages = t3_pkgs[:]
        nearest_neighbor_algorithm(truck3, distances, addresses, query_time)
        afternoon_driver.drive(truck3, truck3.departure_time, min(truck3.current_time, query_time))


    # package 9 special case handling
    pkg_9 = package_hash.search(9)
    address_correction_time = datetime.strptime("10:20", "%H:%M")
    if pkg_9:
        if query_time < address_correction_time:
            pkg_9.address = "300 State St"
            pkg_9.city = "Salt Lake City"
            pkg_9.state = "UT"
            pkg_9.zip_code = "84103"
            pkg_9.delivery_time = None
            pkg_9.left_hub_time = None
        else:
            pkg_9.address = "410 S State St"
            pkg_9.city = "Salt Lake City"
            pkg_9.state = "UT"
            pkg_9.zip_code = "84111"


    return package_hash, t1_pkgs, t2_pkgs, t3_pkgs, [truck1, truck2, truck3], driver_a, driver_b
