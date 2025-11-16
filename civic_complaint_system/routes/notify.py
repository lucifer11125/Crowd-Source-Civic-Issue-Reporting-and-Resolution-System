from flask import flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Complaint
from routes import admin_bp
from routes.auth import role_required

@admin_bp.route('/admin/complaints/<int:id>/notify_department', methods=['POST'])
@login_required
@role_required('admin')
def notify_department(id):
    """Notify department about pending work (admin only)"""
    complaint = Complaint.query.get_or_404(id)

    # Add a status update noting the notification
    complaint.add_status_update(
        updated_by=current_user.id,
        old_status=complaint.status,
        new_status=complaint.status,  # Keep same status
        note='Admin notified department about pending work'
    )

    try:
        db.session.commit()
        flash('Department notified successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to notify department. Please try again.', 'danger')

    return redirect(url_for('admin.all_complaints'))
