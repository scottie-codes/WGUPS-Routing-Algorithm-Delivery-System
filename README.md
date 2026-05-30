# WGUPS Package Delivery Routing Program

**Course:** C950, Data Structures and Algorithms II  
**School:** Western Governors University  

---

## Overview

This program simulates the Western Governors University Parcel Service (WGUPS) delivery scenario, as laid out in the C950 project requirements.  
It uses a custom dynamic hash table and the Nearest Neighbor Algorithm to assign and deliver packages via three trucks and two drivers, following all project constraints and requirements.

### Program Features
- Loads package and address data from CSV files.
- Assigns packages to trucks with custom logic.
- Calculates and displays the most efficient delivery route using the Nearest Neighbor Algorithm.
- Tracks each package’s status (*At Hub*, *Out For Delivery*, *Delivered*) at any user-specified time.
- Reports mileage and trip summary for each driver and truck.
- Automatically resizes the hash table, if needed, to maintain robust speeds.
- Interactive, colored, and specially formatted CLI menu for simulation and status queries.

---

## How to Run

1. **Requirements:**  
   - Python 3.13+ (made and tested with 3.13)
2. **Files:**  
   - All '.py' files, CSVs, screenshots, and this README are in the same directory and ready to run.
3. **Run the Program:**  
   - Open a terminal in the project directory.  
   - Run: 'python main.py' or 'py main.py' depending on your Python installation.

---

## User Instructions

**Main Menu:**
- **Option 1:** View the package and truck status at any time (simulates real-time package delivery).
- **Option 2:** View a final report of mileage and driver/truck activity.
- **Option 0:** Exit the program.

**Screenshots:**  
Screenshots demonstrating program output are included in the 'screenshots' folder.

---

## Notes

**Formatting Inspiration:** Table layouts were inspired by examples from the [tabulate](https://pypi.org/project/tabulate/) Python package.
- No external libraries were used. Just visual inspiration.
---

