#!/usr/bin/env python3
"""
Modern SPA Flask App - Shift Scheduler
Self-contained application with all classes and functions included.
"""

from flask import Flask, render_template_string, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import timedelta, datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from ortools.sat.python import cp_model

app = Flask(__name__)

# Configuration
config_name = os.getenv('FLASK_ENV', 'development')
if config_name == 'production':
    try:
        from config import ProductionConfig
        app.config.from_object(ProductionConfig)
    except ImportError:
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///instance/scheduler.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
else:
    # Development configuration
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/scheduler.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False, default='employee')
    
    # Employee preferences
    max_hours_per_week = db.Column(db.Integer, default=40)
    can_work_weekends = db.Column(db.Boolean, default=True)
    preferred_shift_type = db.Column(db.String(20), default='any')  # 'opening', 'midday', 'closing', 'any'
    
    # Availability (JSON string format)
    availability = db.Column(db.Text)  # Will store JSON of weekly availability
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'max_hours_per_week': self.max_hours_per_week,
            'can_work_weekends': self.can_work_weekends,
            'preferred_shift_type': self.preferred_shift_type,
            'availability': self.availability
        }

class Schedule(db.Model):
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    shift_type = db.Column(db.String(20), nullable=False)  # 'opening', 'midday', 'closing'
    start_time = db.Column(db.String(8), nullable=False)   # Format: "HH:MM"
    end_time = db.Column(db.String(8), nullable=False)     # Format: "HH:MM"
    hours = db.Column(db.Float, nullable=False)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('schedules', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'Unknown',
            'date': self.date.isoformat(),
            'shift_type': self.shift_type,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'hours': self.hours
        }

# Core utility functions
def get_week_dates(week_offset=0):
    """Get start and end dates for a given week offset from current week"""
    today = date.today()
    days_since_monday = today.weekday()
    monday = today - timedelta(days=days_since_monday)
    week_start = monday + timedelta(weeks=week_offset)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end

def calculate_shift_hours(start_time, end_time):
    """Calculate hours between two time strings"""
    start = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")
    
    # Handle overnight shifts
    if end < start:
        end += timedelta(days=1)
    
    delta = end - start
    return delta.total_seconds() / 3600

def generate_shifts(employees, week_start_date, constraints=None):
    """
    Generate optimal shift schedule using OR-Tools
    """
    if not employees:
        return []
    
    # Default shift definitions
    shift_definitions = {
        'opening': {'start': '08:00', 'end': '16:00'},
        'midday': {'start': '12:00', 'end': '20:00'},
        'closing': {'start': '16:00', 'end': '00:00'}
    }
    
    if constraints:
        shift_definitions.update(constraints.get('shift_definitions', {}))
    
    # Days of the week
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    shifts = ['opening', 'midday', 'closing']
    
    schedules = []
    
    try:
        # Create CP-SAT model
        model = cp_model.CpModel()
        
        # Variables: employee_shift[employee][day][shift] = 1 if assigned
        employee_shift = {}
        for emp in employees:
            employee_shift[emp.id] = {}
            for day_idx, day in enumerate(days):
                employee_shift[emp.id][day_idx] = {}
                for shift in shifts:
                    employee_shift[emp.id][day_idx][shift] = model.NewBoolVar(
                        f'emp_{emp.id}_day_{day_idx}_shift_{shift}'
                    )
        
        # Constraints
        
        # 1. Each shift must have at least one employee
        for day_idx in range(7):
            for shift in shifts:
                model.Add(
                    sum(employee_shift[emp.id][day_idx][shift] for emp in employees) >= 1
                )
        
        # 2. Employee weekly hour limits
        for emp in employees:
            weekly_hours = []
            for day_idx in range(7):
                for shift in shifts:
                    shift_hours = calculate_shift_hours(
                        shift_definitions[shift]['start'],
                        shift_definitions[shift]['end']
                    )
                    weekly_hours.append(
                        employee_shift[emp.id][day_idx][shift] * int(shift_hours)
                    )
            
            model.Add(sum(weekly_hours) <= emp.max_hours_per_week or 40)
        
        # 3. No employee works consecutive shifts on the same day
        for emp in employees:
            for day_idx in range(7):
                # Can't work opening and midday on same day
                model.Add(
                    employee_shift[emp.id][day_idx]['opening'] +
                    employee_shift[emp.id][day_idx]['midday'] <= 1
                )
                # Can't work midday and closing on same day
                model.Add(
                    employee_shift[emp.id][day_idx]['midday'] +
                    employee_shift[emp.id][day_idx]['closing'] <= 1
                )
        
        # 4. Weekend constraints
        for emp in employees:
            if not emp.can_work_weekends:
                for shift in shifts:
                    model.Add(employee_shift[emp.id][5][shift] == 0)  # Saturday
                    model.Add(employee_shift[emp.id][6][shift] == 0)  # Sunday
        
        # Solve
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Extract solution
            for emp in employees:
                for day_idx, day in enumerate(days):
                    for shift in shifts:
                        if solver.Value(employee_shift[emp.id][day_idx][shift]) == 1:
                            shift_date = week_start_date + timedelta(days=day_idx)
                            shift_hours = calculate_shift_hours(
                                shift_definitions[shift]['start'],
                                shift_definitions[shift]['end']
                            )
                            
                            schedules.append({
                                'user_id': emp.id,
                                'user_name': emp.name,
                                'date': shift_date,
                                'shift_type': shift,
                                'start_time': shift_definitions[shift]['start'],
                                'end_time': shift_definitions[shift]['end'],
                                'hours': shift_hours
                            })
        
        else:
            # Fallback: Simple round-robin assignment
            for day_idx, day in enumerate(days):
                shift_date = week_start_date + timedelta(days=day_idx)
                for shift_idx, shift in enumerate(shifts):
                    emp_idx = (day_idx + shift_idx) % len(employees)
                    emp = employees[emp_idx]
                    
                    shift_hours = calculate_shift_hours(
                        shift_definitions[shift]['start'],
                        shift_definitions[shift]['end']
                    )
                    
                    schedules.append({
                        'user_id': emp.id,
                        'user_name': emp.name,
                        'date': shift_date,
                        'shift_type': shift,
                        'start_time': shift_definitions[shift]['start'],
                        'end_time': shift_definitions[shift]['end'],
                        'hours': shift_hours
                    })
    
    except Exception as e:
        print(f"OR-Tools error: {e}")
        # Fallback scheduling
        for day_idx, day in enumerate(days):
            shift_date = week_start_date + timedelta(days=day_idx)
            for shift_idx, shift in enumerate(shifts):
                if employees:
                    emp_idx = (day_idx + shift_idx) % len(employees)
                    emp = employees[emp_idx]
                    
                    shift_hours = calculate_shift_hours(
                        shift_definitions[shift]['start'],
                        shift_definitions[shift]['end']
                    )
                    
                    schedules.append({
                        'user_id': emp.id,
                        'user_name': emp.name,
                        'date': shift_date,
                        'shift_type': shift,
                        'start_time': shift_definitions[shift]['start'],
                        'end_time': shift_definitions[shift]['end'],
                        'hours': shift_hours
                    })
    
    return schedules

# Initialize database
def init_db():
    """Initialize database with tables and sample data"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                name='Administrator',
                email='admin@company.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create sample employees
            employees = [
                {'username': 'john_doe', 'name': 'John Doe', 'email': 'john@company.com'},
                {'username': 'jane_smith', 'name': 'Jane Smith', 'email': 'jane@company.com'},
                {'username': 'bob_johnson', 'name': 'Bob Johnson', 'email': 'bob@company.com'},
            ]
            
            for emp_data in employees:
                employee = User(
                    username=emp_data['username'],
                    name=emp_data['name'],
                    email=emp_data['email'],
                    role='employee'
                )
                employee.set_password('password123')
                db.session.add(employee)
            
            db.session.commit()
            print("✅ Database initialized with sample data")

# Routes

@app.route('/')
def index():
    """Serve the main SPA page"""
    with open('index.html', 'r') as f:
        return f.read()

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

# API Routes

@app.route('/api/login', methods=['POST'])
def login():
    """API endpoint for user login"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/employees')
def get_employees():
    """Get all employees"""
    employees = User.query.filter_by(role='employee').all()
    return jsonify([emp.to_dict() for emp in employees])

@app.route('/api/employees', methods=['POST'])
def add_employee():
    """Add new employee"""
    data = request.get_json()
    
    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    
    employee = User(
        username=data['username'],
        name=data['name'],
        email=data['email'],
        phone=data.get('phone', ''),
        role='employee',
        max_hours_per_week=data.get('max_hours_per_week', 40),
        can_work_weekends=data.get('can_work_weekends', True),
        preferred_shift_type=data.get('preferred_shift_type', 'any')
    )
    employee.set_password(data.get('password', 'password123'))
    
    db.session.add(employee)
    db.session.commit()
    
    return jsonify({'success': True, 'employee': employee.to_dict()})

@app.route('/api/employees/<int:emp_id>', methods=['PUT'])
def update_employee(emp_id):
    """Update employee"""
    employee = User.query.get_or_404(emp_id)
    data = request.get_json()
    
    employee.name = data.get('name', employee.name)
    employee.email = data.get('email', employee.email)
    employee.phone = data.get('phone', employee.phone)
    employee.max_hours_per_week = data.get('max_hours_per_week', employee.max_hours_per_week)
    employee.can_work_weekends = data.get('can_work_weekends', employee.can_work_weekends)
    employee.preferred_shift_type = data.get('preferred_shift_type', employee.preferred_shift_type)
    
    if data.get('password'):
        employee.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({'success': True, 'employee': employee.to_dict()})

@app.route('/api/employees/<int:emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    """Delete employee"""
    employee = User.query.get_or_404(emp_id)
    
    # Delete associated schedules
    Schedule.query.filter_by(user_id=emp_id).delete()
    
    db.session.delete(employee)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/schedules')
def get_schedules():
    """Get schedules for a specific week"""
    week_offset = request.args.get('week', 0, type=int)
    week_start, week_end = get_week_dates(week_offset)
    
    schedules = Schedule.query.filter(
        Schedule.date >= week_start,
        Schedule.date <= week_end
    ).order_by(Schedule.date, Schedule.start_time).all()
    
    return jsonify({
        'schedules': [schedule.to_dict() for schedule in schedules],
        'week_start': week_start.isoformat(),
        'week_end': week_end.isoformat()
    })

@app.route('/api/schedules/generate', methods=['POST'])
def generate_schedule():
    """Generate optimized schedule for a week"""
    data = request.get_json()
    week_offset = data.get('week', 0)
    week_start, week_end = get_week_dates(week_offset)
    
    # Get all employees
    employees = User.query.filter_by(role='employee').all()
    
    if not employees:
        return jsonify({'success': False, 'message': 'No employees found'}), 400
    
    # Clear existing schedules for this week
    Schedule.query.filter(
        Schedule.date >= week_start,
        Schedule.date <= week_end
    ).delete()
    
    # Generate new schedules
    generated_schedules = generate_shifts(employees, week_start, data.get('constraints'))
    
    # Save to database
    for schedule_data in generated_schedules:
        schedule = Schedule(
            user_id=schedule_data['user_id'],
            date=schedule_data['date'],
            shift_type=schedule_data['shift_type'],
            start_time=schedule_data['start_time'],
            end_time=schedule_data['end_time'],
            hours=schedule_data['hours']
        )
        db.session.add(schedule)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Generated {len(generated_schedules)} shifts for week starting {week_start.isoformat()}'
    })

@app.route('/api/schedules/<int:schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    """Update a specific schedule"""
    schedule = Schedule.query.get_or_404(schedule_id)
    data = request.get_json()
    
    schedule.shift_type = data.get('shift_type', schedule.shift_type)
    schedule.start_time = data.get('start_time', schedule.start_time)
    schedule.end_time = data.get('end_time', schedule.end_time)
    schedule.hours = calculate_shift_hours(schedule.start_time, schedule.end_time)
    
    db.session.commit()
    
    return jsonify({'success': True, 'schedule': schedule.to_dict()})

@app.route('/api/schedules/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """Delete a specific schedule"""
    schedule = Schedule.query.get_or_404(schedule_id)
    db.session.delete(schedule)
    db.session.commit()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    # Create instance directory if it doesn't exist
    os.makedirs('instance', exist_ok=True)
    
    # Initialize database
    init_db()
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
