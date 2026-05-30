from enum import Enum
from datetime import datetime, timedelta
from constants import TRUCK_CAPACITY, TRUCK_SPEED


class Status(Enum):
    """
    An ENUM representing four possible delivery statuses for a package:
        AT_HUB, EN_ROUTE, DELIVERED, INVALID
    """
    AT_HUB = "At Hub"
    EN_ROUTE = "Out For Delivery"
    DELIVERED = "Delivered"
    INVALID = "Invalid Address"
    DELAYED = "Flight Delayed"

class Package:
    """
    Represents a package object with all associated delivery data and status tracking.

    Args:
        package_id (int): Unique ID for the package.
        address (str): Delivery address.
        city (str): City of delivery.
        state (str): State of delivery.
        zip_code (int): Zip code for delivery.
        deadline (str): Delivery deadline.
        weight (float): Weight of the package.
        notes (str): Optional notes about the package.
        status (Status): Delivery status.
        delivery_time (datetime): Time delivered.
        left_hub_time (datetime): Time package left the hub.
    """

    def __init__(self, package_id, address, city, state, zip_code, deadline,
                 weight, notes="", status=Status.AT_HUB, delivery_time=None, left_hub_time=None):
        # Convert to int for consistent ID handling
        self.package_id = int(package_id)
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.deadline = deadline
        self.weight = weight
        self.notes = notes
        self.status = status
        self.delivery_time = delivery_time
        self.left_hub_time = left_hub_time


class Driver:
    """
    Represents a delivery truck driver and tracks their mileage and truck history.

        Args:
            name (str): The name of the driver.
    """

    def __init__(self, name):
        self.name = name
        self.total_miles = 0.0  # total driver miles
        self.truck_history = []  # list of truck_id, miles, start_time, end_time

    def drive(self, truck, start_time, end_time):
        self.total_miles += truck.miles
        # Adds this truck run to the driver's trip history
        self.truck_history.append((truck.truck_id, truck.miles, start_time.strftime("%H:%M:%S"),end_time.strftime("%H:%M:%S")))


class Truck:
    """
    Simulates a delivery truck and its route, mileage and departure time.

    Args:
        truck_id (str): ID for the truck.
        departure_time (datetime): Time the truck departs the hub.
    """

    def __init__(self, truck_id, departure_time):
        self.truck_id = truck_id
        self.packages = []
        self.capacity = TRUCK_CAPACITY
        self.speed = TRUCK_SPEED
        self.departure_time = departure_time
        self.current_time = departure_time
        self.miles = 0.0
        self.location = 0

    def reset(self, new_departure_time):
        """
        Resets truck state for a new route.
        """

        self.packages = []
        self.departure_time = new_departure_time
        self.current_time = new_departure_time
        self.location = 0
        self.miles = 0.0

    def package_delivery(self, package, distance, address_index):
        """
        Delivers a package and updates truck state.
        Returns the distance traveled.
        """
        # marks when package leaves hub (for lookups)

        if not package.left_hub_time:
            package.left_hub_time = self.current_time
        self.miles += distance  # adds delivery distance to truck's miles
        travel_time = timedelta(hours=(distance / self.speed))  # calculates travel time
        self.current_time += travel_time  # update truck's time with travel time

        # mark package as delivered
        package.status = Status.DELIVERED
        package.delivery_time = self.current_time  # Set when package was delivered
        self.location = address_index  # update current address
        return distance
