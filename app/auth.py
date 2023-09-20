from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required
from models import User
from app import db
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from users_policy import UsersPolicy

bp = Blueprint('auth', __name__, url_prefix='/auth')


def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Для выполнения данного действия необходимо пройти процедуру аутентификации'
    login_manager.login_message_category = 'warning'
    login_manager.user_loader(load_user)
    login_manager.init_app(app)

def load_user(user_id):
    user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar()
    return user

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # try:
        if request.method == 'POST':
            login = request.form.get('login')
            password = request.form.get('password')
            if login and password:
                user = db.session.execute(db.select(User).filter_by(login=login)).scalar()
                if user and user.check_password(password):
                    login_user(user)
                    next = request.args.get('next')
                    return redirect(next or url_for('index'))
            flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')
        return render_template('auth/login.html')
    # except:
    #     flash('Ошибка при загрузке данных')
    #     return redirect(url_for('index'))
        

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            login = request.form.get('login')
            password = request.form.get('password')
            passwordAgain = request.form.get('passwordAgain')
            if password != passwordAgain:
                flash('Пароли не совпадают', 'danger')
            else:
                if login and password:
                    user = db.session.execute(db.select(User).filter_by(login=login)).scalar()
                    if user is None:
                        first_name_form = request.form.get('first_name')
                        last_name_form = request.form.get('last_name')
                        middle_name_form = request.form.get('middle_name')
                        user = User(first_name = first_name_form, last_name = last_name_form, middle_name = middle_name_form, login=login)
                        user.set_password(password)
                        db.session.add(user)
                        db.session.commit()
                        login_user(user)
                        next = request.args.get('next')
                        return redirect(next or url_for('index'))
                    else:
                        print('-------------')
                        flash('Пользователь с таким логином уже существует', 'danger')
        return render_template('auth/register.html')
    except:
        db.session.rollback()
        flash('Ошибка при загрузке данных')
        return redirect(url_for('index'))
        


def check_rights(action):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = None
            user_id = kwargs.get("user_id")
            if user_id:
                user = load_user(user_id)
            if not current_user.can(action, user):
                flash("У вас недостаточно прав для выполнения данного действия", "warning")
                return redirect(url_for('index'))
            return func(*args, **kwargs)
        return wrapper
    return decorator

   
