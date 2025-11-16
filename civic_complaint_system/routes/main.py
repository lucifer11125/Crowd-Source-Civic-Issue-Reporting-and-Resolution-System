from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from models import db, Complaint, User
from routes import main_bp
from sqlalchemy import func
from datetime import datetime, timedelta

@main_bp.route('/')
def index():
    """Landing page with public statistics and recent resolved complaints"""
    # Get public statistics
    total_complaints = Complaint.query.count()
    resolved_complaints = Complaint.query.filter_by(status='resolved').count()
    in_progress_complaints = Complaint.query.filter_by(status='in_progress').count()

    # Calculate resolution rate
    resolution_rate = 0
    if total_complaints > 0:
        resolution_rate = round((resolved_complaints / total_complaints) * 100, 1)

    # Get recent resolved complaints (public)
    recent_resolved = Complaint.query.filter_by(status='resolved')\
        .order_by(Complaint.resolved_at.desc())\
        .limit(5)\
        .all()

    # Get complaints by category for public view
    category_stats = db.session.query(
        Complaint.category,
        func.count(Complaint.id).label('count')
    ).group_by(Complaint.category).all()

    return render_template('index.html',
                         total_complaints=total_complaints,
                         resolved_complaints=resolved_complaints,
                         in_progress_complaints=in_progress_complaints,
                         resolution_rate=resolution_rate,
                         recent_resolved=recent_resolved,
                         category_stats=category_stats)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Role-based dashboard redirect"""
    if current_user.role == 'citizen':
        return redirect(url_for('complaints.citizen_dashboard'))
    elif current_user.role == 'municipal':
        return redirect(url_for('complaints.municipal_dashboard'))
    elif current_user.role == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    else:
        # Fallback for unknown roles
        return redirect(url_for('main.index'))

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@main_bp.route('/help')
def help():
    """Help/FAQ page"""
    return render_template('help.html')

# Error page routes
@main_bp.route('/404')
def not_found():
    """404 error page"""
    return render_template('404.html'), 404

@main_bp.route('/500')
def internal_error():
    """500 error page"""
    return render_template('500.html'), 500

# Utility functions for templates
@main_bp.app_template_filter('get_department_name')
def get_department_name(department_code):
    """Convert department code to readable name"""
    department_names = {
        'roads': 'Roads & Transportation',
        'water': 'Water Supply & Drainage',
        'sanitation': 'Sanitation & Waste Management',
        'general': 'General Administration',
        'administration': 'System Administration'
    }
    return department_names.get(department_code, department_code.title())

@main_bp.app_template_filter('get_category_name')
def get_category_name(category_code):
    """Convert category code to readable name"""
    category_names = {
        'potholes': 'Potholes & Road Damage',
        'streetlight': 'Street Light Issues',
        'garbage': 'Garbage Collection',
        'water_supply': 'Water Supply Issues',
        'drainage': 'Drainage Problems',
        'other': 'Other Issues'
    }
    return category_names.get(category_code, category_code.title())

@main_bp.app_context_processor
def inject_global_vars():
    """Inject global variables into templates"""
    # Get system statistics (cached per request)
    total_complaints = Complaint.query.count()
    resolved_count = Complaint.query.filter_by(status='resolved').count()
    pending_count = Complaint.query.filter(Complaint.status.in_(['submitted', 'in_progress'])).count()

    return {
        'total_complaints': total_complaints,
        'resolved_count': resolved_count,
        'pending_count': pending_count,
        'current_year': datetime.now().year
    }