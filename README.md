# Inventory Management System

## Overview
This is an inventory management system built with Flask. It supports receiving inventory items, printing labels, and managing the inventory through a web interface.

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL

### Setup

1. **Clone the repository:**
    ```sh
    git clone https://github.com/rekk2/Lot_Tracking.git
    cd Lot_tracking
    ```

2. **Create and activate a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up the environment variables:**
    - Create a `.env` file in the root directory of the project and copy the contents of `.env.example` into it.
    - Update the values in `.env` as needed.

5. **Set up the PostgreSQL database:**
    - Create a new PostgreSQL database and user.
    - Update the `SQLALCHEMY_DATABASE_URI` in the `.env` file with your database credentials.

6. **Initialize the database:**
    ```sh
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
    ```

7. **Run the application:**
    ```sh
    flask run
    ```

### PostgreSQL Setup

1. **Install PostgreSQL:**
    - On macOS: `brew install postgresql`
    - On Ubuntu: `sudo apt-get install postgresql postgresql-contrib`
    - On Windows: [Download from the PostgreSQL website](https://www.postgresql.org/download/windows/)

2. **Create a new database and user:**
    ```sh
    sudo -u postgres psql
    CREATE DATABASE inventory_db;
    CREATE USER inventory_user WITH PASSWORD 'yourpassword';
    ALTER ROLE inventory_user SET client_encoding TO 'utf8';
    ALTER ROLE inventory_user SET default_transaction_isolation TO 'read committed';
    ALTER ROLE inventory_user SET timezone TO 'UTC';
    GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;
    \q
    ```

3. **Update the `.env` file with your database credentials:**
    ```
    SQLALCHEMY_DATABASE_URI=postgresql://inventory_user:yourpassword@localhost/inventory_db
    ```

4. **Run the database migrations:**
    ```sh
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
    ```

### Environment Variables

1. **Set up the environment variables:**
    - Create a `.env` file in the root directory of the project and copy the contents of `.env.example` into it.
    - Update the values in `.env` as needed.

2. **Example `.env` file contents:**
    ```env
    # Flask settings
    FLASK_APP=run.py
    FLASK_ENV=development
    SECRET_KEY=your_secret_key

    # Database settings
    SQLALCHEMY_DATABASE_URI=postgresql://username:password@localhost/dbname
    SQLALCHEMY_TRACK_MODIFICATIONS=False

    # Printer settings
    PRINTER_IP=192.168.50.12
    ```

## Usage

- Visit `http://127.0.0.1:5000` in your web browser to access the application.
- Use the web interface to receive items, print labels, and manage inventory.

## Contributing

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature-name`.
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
