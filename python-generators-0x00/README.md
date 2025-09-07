# Python Generators - Task 0

## Project Overview
This project implements a Python script (`seed.py`) to set up a MySQL database (`ALX_prodev`), create a `user_data` table, and populate it with data from a CSV file. It also includes a generator function to stream rows from the `user_data` table one by one, demonstrating the use of Python generators for memory-efficient data processing.

## Repository
- **GitHub Repository**: alx-backend-python
- **Directory**: python-generators-0x00
- **Files**:
  - `seed.py`: Main script with database setup and generator functions.
  - `README.md`: Project documentation.

## Requirements
- Python 3.x
- MySQL Server
- `mysql-connector-python` library (`pip install mysql-connector-python`)
- A `user_data.csv` file with columns: `user_id`, `name`, `email`, `age`

## Setup Instructions
1. Install MySQL and ensure it’s running.
2. Update `seed.py` with your MySQL username and password.
3. Place the `user_data.csv` file in the project directory.
4. Run the provided `0-main.py` to test the script:
   ```bash
   ./0-main.py