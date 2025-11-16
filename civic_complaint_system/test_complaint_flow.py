from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user
from models import db, User, Complaint, StatusUpdate
from config import config
from routes import auth_bp, main_bp, complaints_bp, admin_bp
import os

app = Flask(__name__)
app.config.from_object(config['development'])

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(main_bp, url_prefix='/')
app.register_blueprint(complaints_bp, url_prefix='/')
app.register_blueprint(admin_bp, url_prefix='/')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def test_complaint_flow():
    with app.app_context():
        # Clear existing data and create fresh
        db.drop_all()
        db.create_all()

        # Create test users
        admin = User(
            name='Admin User',
            email='admin@example.com',
            role='admin',
            department='administration'
        )
        admin.set_password('Admin123!')
        db.session.add(admin)

        # Create officers for all departments
        officers_data = [
            {'name': 'John Officer', 'email': 'officer@example.com', 'department': 'roads'},
            {'name': 'Mary Sanitation', 'email': 'sanitation@example.com', 'department': 'sanitation'},
            {'name': 'Bob Water', 'email': 'water@example.com', 'department': 'water'},
            {'name': 'Alice General', 'email': 'general@example.com', 'department': 'general'}
        ]

        officers = []
        for officer_data in officers_data:
            officer = User(
                name=officer_data['name'],
                email=officer_data['email'],
                role='municipal',
                department=officer_data['department']
            )
            officer.set_password('Officer123!')
            db.session.add(officer)
            officers.append(officer)

        citizen = User(
            name='Jane Citizen',
            email='citizen@example.com',
            role='citizen'
        )
        citizen.set_password('Citizen123!')
        db.session.add(citizen)

        db.session.commit()

        print("Test users created.")

        # Simulate complaint submission (like the route does)
        with app.test_request_context():
            from flask_login import login_user
            login_user(citizen)  # Login as citizen

            # Create complaint data
            category = 'potholes'
            description = 'Test pothole complaint'
            address = '123 Test Street'
            landmark = 'Near Test Park'
            priority = 'high'

            complaint = Complaint(
                user_id=citizen.id,
                category=category,
                description=description,
                address=address,
                landmark=landmark,
                priority=priority
            )

            db.session.add(complaint)
            db.session.flush()

            # Auto-assignment logic
            from models import get_auto_assignment_department, find_best_officer_for_assignment
            department = get_auto_assignment_department(category)
            assigned_officer = find_best_officer_for_assignment(department)

            if assigned_officer:
                complaint.assigned_department = department
                complaint.assigned_officer = assigned_officer.id
                complaint.add_status_update(
                    updated_by=assigned_officer.id,
                    old_status='submitted',
                    new_status='submitted',
                    note=f'Auto-assigned to {assigned_officer.name} ({assigned_officer.department} department)'
                )
                print(f"Complaint auto-assigned to {assigned_officer.name} in {assigned_officer.department} department.")
            else:
                complaint.assigned_department = department
                complaint.add_status_update(
                    updated_by=citizen.id,
                    old_status=None,
                    new_status='submitted',
                    note='Complaint submitted and pending assignment'
                )
                print("Complaint submitted but no officer available for assignment.")

            db.session.commit()

            # Check if complaint appears on municipal dashboard
            # Find the assigned officer (John Officer)
            assigned_officer = User.query.filter_by(email='officer@example.com').first()
            municipal_complaints = Complaint.query.filter_by(assigned_officer=assigned_officer.id).all()
            print(f"Complaints assigned to {assigned_officer.name}: {len(municipal_complaints)}")

            for comp in municipal_complaints:
                print(f"- ID: {comp.id}, Category: {comp.category}, Status: {comp.status}, Priority: {comp.priority}")

            # Check citizen dashboard
            citizen_complaints = Complaint.query.filter_by(user_id=citizen.id).all()
            print(f"Complaints by {citizen.name}: {len(citizen_complaints)}")

            for comp in citizen_complaints:
                assigned_name = comp.assigned_officer_rel.name if comp.assigned_officer_rel else 'Unassigned'
                print(f"- ID: {comp.id}, Category: {comp.category}, Status: {comp.status}, Assigned to: {assigned_name}")

if __name__ == '__main__':
    test_complaint_flow()
