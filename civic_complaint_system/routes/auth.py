from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from routes import auth_bp
from datetime import datetime
import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    return True, "Password is valid"

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'citizen')
        department = request.form.get('department', '').strip() if role == 'municipal' else ''

        # Validation
        errors = []

        if not name or len(name) < 2:
            errors.append('Name must be at least 2 characters long')

        if not email or not validate_email(email):
            errors.append('Please enter a valid email address')

        if User.query.filter_by(email=email).first():
            errors.append('Email already registered')

        valid_password, password_msg = validate_password(password)
        if not valid_password:
            errors.append(password_msg)

        if password != confirm_password:
            errors.append('Passwords do not match')

        if role not in ['citizen', 'municipal', 'admin']:
            errors.append('Invalid role selected')

        if role == 'municipal' and not department:
            errors.append('Department is required for municipal officers')

        if role == 'admin' and not department:
            department = 'administration'

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html',
                                 name=name,
                                 email=email,
                                 role=role,
                                 department=department)

        # Create new user
        user = User(
            name=name,
            email=email,
            role=role,
            department=department if department else None
        )
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
            return render_template('register.html',
                                 name=name,
                                 email=email,
                                 role=role,
                                 department=department)

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'

        # Validation
        if not email or not password:
            flash('Please enter both email and password', 'danger')
            return render_template('login.html', email=email)

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password', 'danger')
            return render_template('login.html', email=email)

        if not user.is_active:
            flash('Your account has been deactivated. Please contact administrator.', 'danger')
            return render_template('login.html', email=email)

        # Log in user
        login_user(user, remember=remember_me)

        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Get next page from session or default
        next_page = session.get('next', url_for('main.dashboard'))
        session.pop('next', None)

        # Security: ensure next page is relative
        if next_page and not next_page.startswith('/'):
            next_page = url_for('main.dashboard')

        flash(f'Welcome back, {user.name}!', 'success')
        return redirect(next_page)

    # Store next page for redirect after login
    next_page = request.args.get('next')
    if next_page:
        session['next'] = next_page

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

# Role-based access control decorator
def role_required(required_roles):
    """Decorator to require specific user roles"""
    from functools import wraps
    from flask_login import login_required

    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            roles = required_roles if isinstance(required_roles, list) else [required_roles]

            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('main.dashboard'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator
