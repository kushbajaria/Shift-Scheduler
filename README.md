# Shift Scheduler

A Flask-based web application for managing employee shifts and schedules.

## Features

- **Admin Dashboard**: Create and manage employee schedules
- **Employee Portal**: View personal schedules and profile information
- **Automatic Scheduling**: Generate optimal schedules using OR-Tools
- **User Management**: Add, edit, and remove employees
- **Shift Management**: Flexible shift types (opening, midday, closing)

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/kushbajaria/Shift-Scheduler.git
   cd Shift-Scheduler
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python init_database.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser to `http://localhost:5000`
   - Login with:
     - Username: `admin`
     - Password: `admin123`

### Using the Startup Script

Alternatively, use the startup script that handles database initialization automatically:

```bash
python run.py
```

## Default Login

- **Username**: admin
- **Password**: admin123

⚠️ **Important**: Change the default admin password after the first login!

Download zip folder, open workscheduler folder, then open the terminal to type the following commands.

Create a virtual environment:

- python3 -m venv venv
- source venv/bin/activate
- For Windows: venv\Scripts\activate

After run this command that installs the required packages:

python3 -m pip install -r requirements.txt

Initialize the Database in the terminal, copy the following command: 
- python init_db.py
- Creates the database file for the website
- Default admin user credentials
    - Username: admin
    - Password: password123
- It will create the database file in the instance folder, you would have to create your own set of employees to test out the entire program functionality. If you do not want to create a set of employees, drag the database file from the sample folder into the instance folder that is created when the database was initialized.

Run the program in the terminal, copy the following command:
- python run.py
