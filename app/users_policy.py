from flask_login import current_user
from app import app

class UsersPolicy:
    def __init__(self, record):
        self.record = record
    
    def create_setup(self):
        return current_user.is_authenticated

    def delete_setup(self):
        return current_user.is_admin() or current_user.id == author_id

    def edit_setup(self):
        return current_user.is_admin() or current_user.id == author_id
    
    def admin_panel(self):
        return current_user.role_id == app.config['ADMIN_ROLE_ID']