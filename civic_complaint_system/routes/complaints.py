import os
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Complaint, StatusUpdate, User, get_auto_assignment_department, find_best_officer_for_assignment
from routes import complaints_bp
from routes.auth import role_required

# Valid complaint categories
VALID_CATEGORIES = ['potholes', 'streetlight', 'garbage', 'water_supply', 'drainage', 'other']

# Valid status values
VALID_STATUSES = ['submitted', 'in_progress', 'resolved', 'rejected']

# Valid priority values
VALID_PRIORITIES = ['high', 'medium', 'low']

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def validate_complaint_form(data):
    """Validate complaint form data"""
    errors = []

    if not data.get('category') in VALID_CATEGORIES:
        errors.append('Please select a valid complaint category')

    if not data.get('description') or len(data.get('description', '').strip()) < 10:
        errors.append('Description must be at least 10 characters long')

    if not data.get('address') or len(data.get('address', '').strip()) < 5:
        errors.append('Please provide a valid address')

    if not data.get('priority') in VALID_PRIORITIES:
        errors.append('Please select a valid priority level')

    return errors

@complaints_bp.route('/complaints/new', methods=['GET', 'POST'])
@login_required
@role_required('citizen')
def new_complaint():
    """Submit new complaint (citizens only)"""
    if request.method == 'POST':
        # Get form data
        category = request.form.get('category')
        description = request.form.get('description')
        address = request.form.get('address')
        landmark = request.form.get('landmark', '').strip()
        priority = request.form.get('priority', 'medium')

        # Validate form
        errors = validate_complaint_form({
            'category': category,
            'description': description,
            'address': address,
            'priority': priority
        })

        # Handle file upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                if not allowed_file(file.filename):
                    errors.append('Invalid file type. Only PNG, JPG, JPEG, and GIF files are allowed.')
                elif file.content_length > current_app.config['MAX_CONTENT_LENGTH']:
                    errors.append('File size too large. Maximum size is 5MB.')
                else:
                    # Secure and save file
                    filename = secure_filename(file.filename)
                    # Add timestamp to prevent conflicts
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    image_filename = f"{timestamp}_{filename}"
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
                    file.save(file_path)

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('complaint_form.html',
                                 category=category,
                                 description=description,
                                 address=address,
                                 landmark=landmark,
                                 priority=priority)

        # Create complaint
        complaint = Complaint(
            user_id=current_user.id,
            category=category,
            description=description,
            address=address,
            landmark=landmark if landmark else None,
            image_filename=image_filename,
            priority=priority
        )

        try:
            db.session.add(complaint)
            db.session.flush()  # Get the complaint ID

            # Auto-assignment logic - assign to department only
            department = get_auto_assignment_department(category)
            complaint.assigned_department = department

            # Add status update for department assignment
            complaint.add_status_update(
                updated_by=current_user.id,
                old_status=None,
                new_status='submitted',
                note=f'Complaint submitted to {department} department'
            )
            flash(f'Complaint submitted successfully! Assigned to {department} department.', 'success')

            db.session.commit()
            return redirect(url_for('complaints.citizen_dashboard'))

        except Exception as e:
            db.session.rollback()
            # Clean up uploaded file if database operation failed
            if image_filename:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            flash('Failed to submit complaint. Please try again.', 'danger')
            return render_template('complaint_form.html',
                                 category=category,
                                 description=description,
                                 address=address,
                                 landmark=landmark,
                                 priority=priority)

    return render_template('complaint_form.html')

@complaints_bp.route('/complaints/<int:id>')
@login_required
def view_complaint(id):
    """View complaint details with timeline"""
    complaint = Complaint.query.get_or_404(id)

    # Check access permissions
    if current_user.role == 'citizen' and complaint.user_id != current_user.id:
        flash('You can only view your own complaints.', 'danger')
        return redirect(url_for('complaints.citizen_dashboard'))

    if current_user.role == 'municipal' and complaint.assigned_department != current_user.department:
        flash('You can only view complaints assigned to your department.', 'danger')
        return redirect(url_for('complaints.municipal_dashboard'))

    # Admins can view all complaints

    # No need to load officer data since we assign to departments

    # Get status updates (timeline)
    status_updates = complaint.get_status_history()

    return render_template('view_complaint.html',
                         complaint=complaint,
                         status_updates=status_updates)

@complaints_bp.route('/complaints/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(['municipal', 'admin'])
def edit_complaint(id):
    """Update complaint status (municipal officers, admin)"""
    complaint = Complaint.query.get_or_404(id)

    # Check access permissions
    if current_user.role == 'municipal' and complaint.assigned_department != current_user.department:
        flash('You can only edit complaints assigned to your department.', 'danger')
        return redirect(url_for('complaints.municipal_dashboard'))

    if request.method == 'POST':
        new_status = request.form.get('status')
        note = request.form.get('note', '').strip()
        resolution_notes = request.form.get('resolution_notes', '').strip()

        # Validate status
        if new_status not in VALID_STATUSES:
            flash('Invalid status selected.', 'danger')
            return redirect(url_for('complaints.view_complaint', id=complaint.id))

        old_status = complaint.status

        # Update complaint
        complaint.status = new_status
        if new_status == 'resolved' and resolution_notes:
            complaint.resolution_notes = resolution_notes
        elif new_status != 'resolved':
            complaint.resolution_notes = None

        # Add status update to timeline
        update_note = note
        if new_status == 'resolved' and resolution_notes:
            update_note = f"{note}\nResolution: {resolution_notes}" if note else resolution_notes

        complaint.add_status_update(
            updated_by=current_user.id,
            old_status=old_status,
            new_status=new_status,
            note=update_note
        )

        try:
            db.session.commit()
            flash('Complaint status updated successfully!', 'success')
            return redirect(url_for('complaints.view_complaint', id=complaint.id))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update complaint. Please try again.', 'danger')
            return redirect(url_for('complaints.view_complaint', id=complaint.id))

    return render_template('edit_complaint.html', complaint=complaint)

@complaints_bp.route('/complaints/<int:id>/assign', methods=['POST'])
@login_required
@role_required('admin')
def assign_complaint(id):
    """Manual assignment (admin only)"""
    complaint = Complaint.query.get_or_404(id)
    assigned_to = request.form.get('assigned_to', type=int)

    if not assigned_to:
        flash('Please select an officer to assign.', 'danger')
        return redirect(url_for('complaints.view_complaint', id=complaint.id))

    # Get assigned officer
    officer = User.query.get(assigned_to)
    if not officer or officer.role != 'municipal':
        flash('Invalid officer selected.', 'danger')
        return redirect(url_for('complaints.view_complaint', id=complaint.id))

    old_assigned = complaint.assigned_officer
    complaint.assigned_officer = assigned_to

    # Add status update
    old_officer_name = User.query.get(old_assigned).name if old_assigned else 'Unassigned'
    note = f'Reassigned from {old_officer_name} to {officer.name} ({officer.department})'

    complaint.add_status_update(
        updated_by=current_user.id,
        old_status=complaint.status,
        new_status=complaint.status,
        note=note
    )

    try:
        db.session.commit()
        flash(f'Complaint assigned to {officer.name} successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to assign complaint. Please try again.', 'danger')

    return redirect(url_for('complaints.view_complaint', id=complaint.id))

@complaints_bp.route('/complaints/citizen/dashboard')
@login_required
@role_required('citizen')
def citizen_dashboard():
    """Citizen dashboard - shows user's own complaints"""
    status_filter = request.args.get('status', 'all')

    # Base query for user's complaints
    query = Complaint.query.filter_by(user_id=current_user.id)

    # Apply status filter
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    complaints = query.order_by(Complaint.created_at.desc()).all()

    # Get statistics
    total_complaints = Complaint.query.filter_by(user_id=current_user.id).count()
    resolved_count = Complaint.query.filter_by(user_id=current_user.id, status='resolved').count()
    pending_count = Complaint.query.filter(
        Complaint.user_id == current_user.id,
        Complaint.status.in_(['submitted', 'in_progress'])
    ).count()

    return render_template('citizen_dashboard.html',
                         complaints=complaints,
                         status_filter=status_filter,
                         total_complaints=total_complaints,
                         resolved_count=resolved_count,
                         pending_count=pending_count)

@complaints_bp.route('/complaints/municipal/dashboard')
@login_required
@role_required('municipal')
def municipal_dashboard():
    """Municipal officer dashboard - shows complaints assigned to department"""
    status_filter = request.args.get('status', 'all')
    priority_filter = request.args.get('priority', 'all')

    # Base query for complaints assigned to officer's department
    query = Complaint.query.filter_by(assigned_department=current_user.department)

    # Apply filters
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    if priority_filter != 'all':
        query = query.filter_by(priority=priority_filter)

    complaints = query.order_by(Complaint.priority.desc(), Complaint.created_at.desc()).all()

    # Get department-wide statistics
    total_assigned = Complaint.query.filter_by(assigned_department=current_user.department).count()
    resolved_today = Complaint.query.filter(
        Complaint.assigned_department == current_user.department,
        Complaint.status == 'resolved',
        Complaint.resolved_at >= datetime.utcnow().date()
    ).count()
    pending_count = Complaint.query.filter(
        Complaint.assigned_department == current_user.department,
        Complaint.status.in_(['submitted', 'in_progress'])
    ).count()

    return render_template('municipal_dashboard.html',
                         complaints=complaints,
                         status_filter=status_filter,
                         priority_filter=priority_filter,
                         total_assigned=total_assigned,
                         resolved_today=resolved_today,
                         pending_count=pending_count,
                         department=current_user.department)
