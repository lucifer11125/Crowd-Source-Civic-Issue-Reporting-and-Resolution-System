import os
from flask import Flask
from flask_login import LoginManager
from models import db, User
from config import config

def create_app(config_name=None):
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create upload directory if it doesn't exist
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Register blueprints
    from routes import auth_bp, main_bp, complaints_bp, admin_bp
    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(complaints_bp, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/')

    # Custom template functions
    @app.template_filter('datetime')
    def datetime_filter(value, format='%Y-%m-%d %H:%M'):
        if value is None:
            return ''
        return value.strftime(format)

    @app.template_filter('relativetime')
    def relativetime_filter(value):
        from datetime import datetime
        if value is None:
            return ''

        now = datetime.utcnow()
        diff = now - value

        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "Just now"

    @app.template_filter('datetime_obj')
    def datetime_obj_filter(value):
        from datetime import datetime
        if value is None:
            return datetime.utcnow()
        return value

    @app.template_filter('status_badge_class')
    def status_badge_class(status):
        status_classes = {
            'submitted': 'secondary',
            'in_progress': 'primary',
            'resolved': 'success',
            'rejected': 'danger'
        }
        return status_classes.get(status, 'secondary')

    @app.template_filter('priority_badge_class')
    def priority_badge_class(priority):
        priority_classes = {
            'high': 'danger',
            'medium': 'warning',
            'low': 'success'
        }
        return priority_classes.get(priority, 'secondary')

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('500.html'), 500

    return app

def init_db(app):
    """Initialize database with tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

        # Create sample data if no users exist
        if User.query.count() == 0:
            print("Creating sample data...")
            from test_data import create_sample_data
            create_sample_data()

if __name__ == '__main__':
    app = create_app()

    # Initialize database if it doesn't exist
    if not os.path.exists('instance'):
        os.makedirs('instance')

    init_db(app)

    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)