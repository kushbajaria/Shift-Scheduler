# Shift Scheduler - Modern SPA

A modern Single Page Application (SPA) for managing employee shifts and schedules, built with Flask backend and dynamic frontend.

## ✨ Features

- **🌟 Modern SPA Architecture**: Lightning-fast navigation with no page reloads
- **🏢 Admin Dashboard**: Create and manage employee schedules with real-time updates
- **👥 Employee Portal**: View personal schedules and profile information
- **🤖 Smart Scheduling**: Generate optimal schedules using OR-Tools optimization
- **👨‍💼 User Management**: Add, edit, and remove employees with role-based access
- **⚡ Flexible Shifts**: Support for opening, midday, and closing shift types
- **📱 Mobile Responsive**: Works perfectly on all devices

## 🚀 Quick Start

### Easy One-Command Setup

1. **Clone and setup**:
   ```bash
   git clone https://github.com/kushbajaria/Shift-Scheduler.git
   cd Shift-Scheduler
   ```

2. **Run the SPA**:
   ```bash
   python run.py
   ```
   This automatically:
   - Installs required packages
   - Sets up the database
   - Starts the SPA server
   - Opens your browser

3. **Login and start scheduling**:
   - Username: `admin`
   - Password: `admin123`

## 🏗️ Modern SPA Architecture

- **Backend**: Flask API server (`app.py`) with SQLite database
- **Frontend**: Dynamic Single Page Application with real-time updates
- **Smart Optimization**: OR-Tools powered schedule generation
- **Zero Configuration**: Everything works out of the box

### Using the Startup Script

Alternatively, use the startup script that handles database initialization automatically:

```bash
python run.py
```

## Deployment

### Heroku Deployment

1. **Create a Heroku app**
   ```bash
   heroku create your-app-name
   ```

2. **Set environment variables**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-super-secret-key-here
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

4. **Initialize the database**
   ```bash
   heroku run python init_database.py
   ```

### Render Deployment

1. **Connect your GitHub repository to Render**
2. **Set environment variables**:
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: `your-super-secret-key-here`
3. **Build command**: `pip install -r requirements.txt`
4. **Start command**: `gunicorn app:app`

### Environment Variables

- `FLASK_ENV`: Set to `production` for production deployment
- `SECRET_KEY`: A secure secret key for session management
- `DATABASE_URL`: Database connection string (auto-set by most hosting providers)
- `PORT`: Port to run the application on (auto-set by most hosting providers)

## Default Login

- **Username**: admin
- **Password**: admin123

⚠️ **Important**: Change the default admin password after first login!er

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
- python app.py

Go to http://127.0.0.1:5000/ in your web browser to test it out!
