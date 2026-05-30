# ==================================================================
# WGUPS ROUTING PROGRAM IMPLEMENTATION: NHP3 Task 2
# Student: Scott Curtis
# Student ID: 001079564
# Course: C950: Data Structures and Algorithms II
# Western Governors University
# Degree: Computer Science, 2025
# Program Mentor: DeNece Meyer
# ==================================================================
# Table output formatting was inspired by styles from pypi.org/project/tabulate, however library was not used


from datetime import datetime
from simulation import simulate_to_time
from constants import *
from models import Truck, Driver
from hash_table import DynamicHashTable
from routing_algorithms import nearest_neighbor_algorithm, assign_packages_to_trucks
from utils import load_distance_matrix_data, load_package_data, get_time_from_user, clear_screen
from output import print_title, print_package_status_summary_table, print_mileage_and_driver_report, print_current_truck_status


def main_menu(package_hash, t1_pkgs, t2_pkgs, t3_pkgs, trucks, driver_a, driver_b):
    """
    Displays the main menu for user interaction and handles menu selection logic.

    Args:
        package_hash (DynamicHashTable): Hash table of all packages.
        t1_pkgs, t2_pkgs, t3_pkgs (list): Lists of packages on each truck.
        trucks (list): List of Truck objects.
    """
    # infinite menu loop to that lets user interact with simulation output and menu until 'Exit Program' (0) is selected
    while True:
        clear_screen()  # clears previous output for better appearance each time
        print_title()
        print(f"{BOLD}{CYAN}MAIN MENU{RESET}")
        print("1. Package/Truck Status At A Specific Time")
        print("2. Truck & Driver Mileage Report (Final State)")
        print("0. Exit")
        choice = input(f"{GREEN}Enter an option: {RESET}").strip()
        # input validation to make sure valid options are chosen
        if choice not in {"0", "1", "2"}:
            print(f"{RED}Invalid Input: Please type a valid number option and push enter.{RESET}")
            continue

        if choice == "1":
            # Lets user select a time to see full package simulation at that time
            t = get_time_from_user()
            # Run simulation to that time and get the results
            package_hash_sim, t1_pkgs_sim, t2_pkgs_sim, t3_pkgs_sim, trucks_sim, driver_a_sim, driver_b_sim = simulate_to_time(t)
            clear_screen()  # Clears screen for fresh Main Menu
            print_title()
            print_package_status_summary_table(package_hash_sim, t1_pkgs_sim, t2_pkgs_sim, t3_pkgs_sim, t)
            print_current_truck_status(trucks_sim, [driver_a_sim, driver_b_sim], t)
            input(f"\n{GREEN}Press ENTER at any time to return to the MAIN MENU")

        elif choice == "2":
            # displays end of day mileage and driver report
            clear_screen()
            print_title()
            print_mileage_and_driver_report(trucks, [driver_a, driver_b])
            input(f"\n{GREEN}Press ENTER at any time to return to the MAIN MENU")

        elif choice == "0":
            # program exit
            clear_screen()
            print_title()
            print(f"\n{CYAN}Thank you for using the WGUPS Package Delivery System.\nEXITING PROGRAM {RESET}\n")
            break


def main():
    """
    Entry point of the program; initializes data and starts the menu interface.
    """
    full_day_time = datetime.strptime("23:59", "%H:%M")
    package_hash, t1_pkgs, t2_pkgs, t3_pkgs, trucks, driver_a, driver_b = simulate_to_time(full_day_time)

    # print main menu
    main_menu(package_hash, t1_pkgs, t2_pkgs, t3_pkgs, trucks, driver_a, driver_b)

if __name__ == "__main__":
    main()
