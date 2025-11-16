from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Index

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='citizen')
    department = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    complaints = db.relationship('Complaint', backref='user', lazy=True, foreign_keys='Complaint.user_id')
    assigned_complaints = db.relationship('Complaint', backref='assigned_officer_rel', lazy=True, foreign_keys='Complaint.assigned_officer')
    status_updates = db.relationship('StatusUpdate', backref='updater', lazy=True, foreign_keys='StatusUpdate.updated_by')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_municipal_officer(self):
        return self.role == 'municipal'

    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.email}>'

class Complaint(db.Model):
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_department = db.Column(db.String(50), nullable=True)
    assigned_officer = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Keep for backward compatibility
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    landmark = db.Column(db.String(255), nullable=True)
    image_filename = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='submitted')
    priority = db.Column(db.String(10), default='medium')
    resolution_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    status_updates = db.relationship('StatusUpdate', backref='complaint', lazy=True, cascade='all, delete-orphan')

    # Indexes for better query performance
    __table_args__ = (
        Index('idx_status_priority', 'status', 'priority'),
        Index('idx_category_status', 'category', 'status'),
        Index('idx_department_status', 'assigned_department', 'status'),
        Index('idx_assigned_status', 'assigned_officer', 'status'),
    )

    def get_status_history(self):
        """Return all status updates ordered by timestamp"""
        return StatusUpdate.query.filter_by(complaint_id=self.id).order_by(StatusUpdate.timestamp.desc()).all()

    def add_status_update(self, updated_by, old_status, new_status, note=None):
        """Add a new status update to the timeline"""
        update = StatusUpdate(
            complaint_id=self.id,
            updated_by=updated_by,
            old_status=old_status,
            new_status=new_status,
            note=note
        )
        db.session.add(update)

        # Update complaint timestamps
        self.updated_at = datetime.utcnow()
        if new_status == 'resolved':
            self.resolved_at = datetime.utcnow()

        return update

    def __repr__(self):
        return f'<Complaint {self.id}: {self.category}>'

class StatusUpdate(db.Model):
    __tablename__ = 'status_updates'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    old_status = db.Column(db.String(20), nullable=True)
    new_status = db.Column(db.String(20), nullable=False)
    note = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<StatusUpdate {self.id}: {self.old_status} -> {self.new_status}>'

# Helper functions for auto-assignment
def get_auto_assignment_department(category):
    """Get department for a given complaint category"""
    from config import Config
    return Config.CATEGORY_DEPARTMENT_MAP.get(category, 'general')

def find_best_officer_for_assignment(department):
    """Find the municipal officer with the fewest active complaints in a department"""
    officers = User.query.filter_by(
        role='municipal',
        department=department,
        is_active=True
    ).all()

    if not officers:
        # If no officers in specific department, find any municipal officer
        officers = User.query.filter_by(
            role='municipal',
            is_active=True
        ).all()

    if not officers:
        return None

    # Count active complaints for each officer
    officer_counts = []
    for officer in officers:
        active_count = Complaint.query.filter_by(
            assigned_officer=officer.id,
            status='in_progress'
        ).count()
        officer_counts.append((officer, active_count))

    # Return officer with fewest active complaints
    return min(officer_counts, key=lambda x: x[1])[0]
