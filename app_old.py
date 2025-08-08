#!/usr/bin/env python3
"""
Modified Flask app that serves index.html as the main entry point
while keeping the backend API functionality
"""

from flask import Flask, render_template_string, jsonify, request, send_from_directory
import os
from datetime import timedelta, datetime, date

from workscheduler.classes import User, Schedule, db
from workscheduler.core import generate_shifts, get_week_dates

app = Flask(__name__)

# Configuration
config_name = os.getenv('FLASK_ENV', 'development')
if config_name == 'production':
    from config import ProductionConfig
    app.config.from_object(ProductionConfig)
else:
    from config import DevelopmentConfig
    app.config.from_object(DevelopmentConfig)

# Override with environment variables if they exist
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', app.config['SECRET_KEY'])
database_url = os.environ.get('DATABASE_URL')
if database_url:
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

# Initialize the database
db.init_app(app)

# Create tables if they don't exist (only in development)
if config_name != 'production':
    with app.app_context():
        db.create_all()

# Serve index.html as the main page
@app.route('/')
def index():
    """Serve the main index.html file"""
    with open('index.html', 'r') as f:
        return f.read()

# Serve static files
@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('workscheduler/static', filename)

# API Routes (for dynamic functionality)
@app.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for login"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        return jsonify({
            'success': True,
            'user': {
                'username': user.username,
                'firstName': user.first_name,
                'lastName': user.last_name,
                'email': user.email,
                'phone': user.phone,
                'role': user.role
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/schedules/<username>')
def api_schedules(username):
    """API endpoint to get user schedules"""
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get current week dates
    week_dates = get_week_dates()
    schedules = Schedule.query.filter_by(username=username).filter(
        Schedule.date.in_([d.strftime('%Y-%m-%d') for d in week_dates])
    ).all()
    
    schedule_data = []
    for schedule in schedules:
        schedule_data.append({
            'date': schedule.date,
            'startTime': schedule.start_time,
            'endTime': schedule.end_time,
            'day': datetime.strptime(schedule.date, '%Y-%m-%d').strftime('%A')
        })
    
    return jsonify(schedule_data)

@app.route('/api/employees')
def api_employees():
    """API endpoint to get all employees"""
    employees = User.query.filter(User.role != 'admin').all()
    employee_data = []
    
    for emp in employees:
        employee_data.append({
            'username': emp.username,
            'firstName': emp.first_name,
            'lastName': emp.last_name,
            'email': emp.email,
            'phone': emp.phone,
            'role': emp.role,
            'jobAssignment': emp.job_assignment,
            'hourlyRate': emp.hourly_rate
        })
    
    return jsonify(employee_data)

@app.route('/api/generate-schedule', methods=['POST'])
def api_generate_schedule():
    """API endpoint to generate schedules"""
    data = request.get_json()
    
    employees = User.query.filter(User.role != 'admin').all()
    if not employees:
        return jsonify({'success': False, 'message': 'No employees found'}), 400
    
    # Default day requirements if not provided
    day_requirements = data.get('dayRequirements', {
        'monday': {'opening': 1, 'midday': 1, 'closing': 1},
        'tuesday': {'opening': 1, 'midday': 1, 'closing': 1},
        'wednesday': {'opening': 1, 'midday': 1, 'closing': 1},
        'thursday': {'opening': 1, 'midday': 1, 'closing': 1},
        'friday': {'opening': 2, 'midday': 2, 'closing': 2},
        'saturday': {'opening': 2, 'midday': 2, 'closing': 2},
        'sunday': {'opening': 1, 'midday': 1, 'closing': 1}
    })
    
    max_shifts = data.get('maxShifts', 5)
    active_employees = [emp.username for emp in employees]
    
    success = generate_shifts(
        day_requirements=day_requirements,
        max_shifts_per_employee=max_shifts,
        active_employees=active_employees,
        start_date=date.today().strftime('%Y-%m-%d')
    )
    
    if success:
        return jsonify({'success': True, 'message': 'Schedules generated successfully'})
    else:
        return jsonify({'success': False, 'message': 'No feasible schedule found'}), 400

# For any other routes, serve index.html (SPA behavior)
@app.errorhandler(404)
def not_found(error):
    """Serve index.html for any 404 errors (SPA routing)"""
    with open('index.html', 'r') as f:
        return f.read()

if __name__ == '__main__':
    # Create admin user if running directly and in development
    with app.app_context():
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                first_name='Admin',
                last_name='User',
                email='admin@example.com',
                phone='555-1234',
                address='123 Admin St',
                sick_hours=0,
                pto_hours=0,
                hourly_rate=0,
                job_assignment='Administrator',
                hire_date='2020-01-15',
                role='admin'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created - Username: admin, Password: admin123")
    
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=(config_name != 'production'), host='0.0.0.0', port=port)
