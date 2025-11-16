from flask import Blueprint

# Create blueprints
auth_bp = Blueprint('auth', __name__)
main_bp = Blueprint('main', __name__)
complaints_bp = Blueprint('complaints', __name__)
admin_bp = Blueprint('admin', __name__)

# Import routes to register them with blueprints
from . import auth
from . import main
from . import complaints
from . import admin
from . import notify
