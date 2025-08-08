/**
 * Enhanced JavaScript for the SPA version of Shift Scheduler
 * This version connects to the Flask API for real data
 */

class ShiftSchedulerApp {
    constructor() {
        this.currentUser = null;
        this.currentPage = 'login';
        this.init();
    }

    init() {
        this.showPage('login');
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Add any global event listeners here
        document.addEventListener('DOMContentLoaded', () => {
            this.showPage('login');
        });
    }

    async login(event) {
        event.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();
            
            if (data.success) {
                this.currentUser = data.user;
                this.showPage('home');
                document.getElementById('navbar').classList.remove('hidden');
                
                // Show admin menu if user is admin
                if (this.currentUser.role === 'admin') {
                    document.getElementById('admin-menu').classList.remove('hidden');
                    document.getElementById('admin-actions').classList.remove('hidden');
                }
                
                // Update welcome message
                document.getElementById('welcome-message').innerHTML = 
                    `<p>Hello, ${this.currentUser.firstName} ${this.currentUser.lastName}!</p>
                     <p>Role: ${this.currentUser.role}</p>`;
                
                this.loadUserProfile();
            } else {
                this.showError('login-error', data.message || 'Invalid username or password');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showError('login-error', 'Login failed. Please try again.');
        }
    }

    logout() {
        this.currentUser = null;
        this.showPage('login');
        document.getElementById('navbar').classList.add('hidden');
        document.getElementById('admin-menu').classList.add('hidden');
        document.getElementById('admin-actions').classList.add('hidden');
        // Reset form
        document.getElementById('username').value = '';
        document.getElementById('password').value = '';
        this.hideError('login-error');
    }

    showPage(pageName) {
        // Hide all pages
        const pages = ['login-page', 'home-page', 'schedules-page', 'employees-page', 'profile-page'];
        pages.forEach(page => {
            document.getElementById(page).classList.add('hidden');
        });
        
        // Show requested page
        if (pageName === 'login') {
            document.getElementById('login-page').classList.remove('hidden');
        } else {
            document.getElementById(pageName + '-page').classList.remove('hidden');
            
            // Load page-specific content
            if (pageName === 'schedules') {
                this.loadSchedules();
            } else if (pageName === 'employees') {
                this.loadEmployees();
            }
        }
        
        this.currentPage = pageName;
    }

    async loadSchedules() {
        if (!this.currentUser) return;
        
        try {
            const response = await fetch(`/api/schedules/${this.currentUser.username}`);
            const schedules = await response.json();
            
            const tbody = document.getElementById('schedule-tbody');
            tbody.innerHTML = '';
            
            if (schedules.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">No schedules found for this week</td></tr>';
                return;
            }
            
            schedules.forEach(schedule => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${this.formatDate(schedule.date)}</td>
                    <td>${schedule.day}</td>
                    <td>${schedule.startTime} - ${schedule.endTime}</td>
                    <td>${this.calculateHours(schedule.startTime, schedule.endTime)}</td>
                `;
            });
        } catch (error) {
            console.error('Error loading schedules:', error);
            document.getElementById('schedule-tbody').innerHTML = 
                '<tr><td colspan="4" style="text-align: center; color: red;">Error loading schedules</td></tr>';
        }
    }

    async loadEmployees() {
        if (!this.currentUser || this.currentUser.role !== 'admin') return;
        
        try {
            const response = await fetch('/api/employees');
            const employees = await response.json();
            
            const tbody = document.getElementById('employees-tbody');
            tbody.innerHTML = '';
            
            employees.forEach(employee => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${employee.username}</td>
                    <td>${employee.firstName} ${employee.lastName}</td>
                    <td>${employee.email}</td>
                    <td>${employee.role}</td>
                    <td>
                        <button class="btn" onclick="app.editEmployee('${employee.username}')">Edit</button>
                    </td>
                `;
            });
        } catch (error) {
            console.error('Error loading employees:', error);
            document.getElementById('employees-tbody').innerHTML = 
                '<tr><td colspan="5" style="text-align: center; color: red;">Error loading employees</td></tr>';
        }
    }

    loadUserProfile() {
        if (!this.currentUser) return;
        
        document.getElementById('first_name').value = this.currentUser.firstName || '';
        document.getElementById('last_name').value = this.currentUser.lastName || '';
        document.getElementById('email').value = this.currentUser.email || '';
        document.getElementById('phone').value = this.currentUser.phone || '';
    }

    async updateProfile(event) {
        event.preventDefault();
        // In a real implementation, this would send data to the backend
        this.showSuccess('Profile updated successfully!');
    }

    async generateSchedule() {
        if (!this.currentUser || this.currentUser.role !== 'admin') return;
        
        try {
            const response = await fetch('/api/generate-schedule', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    maxShifts: 5,
                    dayRequirements: {
                        'monday': {'opening': 1, 'midday': 1, 'closing': 1},
                        'tuesday': {'opening': 1, 'midday': 1, 'closing': 1},
                        'wednesday': {'opening': 1, 'midday': 1, 'closing': 1},
                        'thursday': {'opening': 1, 'midday': 1, 'closing': 1},
                        'friday': {'opening': 2, 'midday': 2, 'closing': 2},
                        'saturday': {'opening': 2, 'midday': 2, 'closing': 2},
                        'sunday': {'opening': 1, 'midday': 1, 'closing': 1}
                    }
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.showSuccess(data.message);
                // Reload schedules if on schedules page
                if (this.currentPage === 'schedules') {
                    this.loadSchedules();
                }
            } else {
                this.showError('general-error', data.message);
            }
        } catch (error) {
            console.error('Error generating schedule:', error);
            this.showError('general-error', 'Failed to generate schedule');
        }
    }

    // Utility functions
    formatDate(dateString) {
        const date = new Date(dateString + 'T00:00:00');
        return date.toLocaleDateString('en-US', { 
            weekday: 'short', 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
    }

    calculateHours(startTime, endTime) {
        const start = new Date(`1970-01-01T${startTime}:00`);
        const end = new Date(`1970-01-01T${endTime}:00`);
        const diff = (end - start) / (1000 * 60 * 60);
        return diff + ' hours';
    }

    showError(elementId, message) {
        const errorDiv = document.getElementById(elementId);
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.classList.remove('hidden');
        }
    }

    hideError(elementId) {
        const errorDiv = document.getElementById(elementId);
        if (errorDiv) {
            errorDiv.classList.add('hidden');
        }
    }

    showSuccess(message) {
        // Create a temporary success message
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success';
        successDiv.textContent = message;
        successDiv.style.position = 'fixed';
        successDiv.style.top = '20px';
        successDiv.style.right = '20px';
        successDiv.style.zIndex = '1000';
        
        document.body.appendChild(successDiv);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.parentNode.removeChild(successDiv);
            }
        }, 3000);
    }

    editEmployee(username) {
        alert(`Edit employee: ${username} (Feature would be implemented here)`);
    }

    showAddEmployee() {
        alert('Add employee form would be shown here');
    }
}

// Initialize the app
const app = new ShiftSchedulerApp();

// Global functions for HTML onclick handlers
function login(event) {
    app.login(event);
}

function logout() {
    app.logout();
}

function showPage(pageName) {
    app.showPage(pageName);
}

function updateProfile(event) {
    app.updateProfile(event);
}

function generateSchedule() {
    app.generateSchedule();
}

function editEmployee(username) {
    app.editEmployee(username);
}

function showAddEmployee() {
    app.showAddEmployee();
}
