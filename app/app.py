from flask import Flask, render_template, request, send_from_directory, flash
from sqlalchemy import MetaData, desc
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import math

app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)

from auth import bp as auth_bp, init_login_manager
from setups import bp as setups_bp
from user import bp as users_bp
from fuel import bp as fuel_bp

app.register_blueprint(auth_bp)
app.register_blueprint(setups_bp)
app.register_blueprint(users_bp)
app.register_blueprint(fuel_bp)


init_login_manager(app)

from models import Setup, Car, Track
from tools import filtered_setups

def search_params():
    return {
        'car_id': request.args.get('car'),
        'track_id': request.args.get('track'),
    }

@app.route('/')
def index():
    try:
        page = request.args.get('page', 1, type=int)
        setups = db.session.execute(filtered_setups(search_params()).order_by(Setup.created_at).limit(app.config['SETUPS_PER_PAGE_INDEX']).offset(app.config['SETUPS_PER_PAGE_INDEX'] * (page - 1))).scalars()

        setup_count = len(db.session.execute(filtered_setups(search_params())).all())
        
        page_count = math.ceil(setup_count / app.config['SETUPS_PER_PAGE_INDEX'])

        if page_count == 0:
              page_count = 1

        cars = db.session.execute(db.select(Car)).scalars()
        tracks = db.session.execute(db.select(Track)).scalars()

        return render_template(
        'index.html',
        page = page,
        page_count = page_count,
        setups=setups,
        cars=cars,
        tracks=tracks,
        search_params = search_params()
        )
    except:
        flash('Ошибка при загрузке данных', 'danger')
        return render_template(
        'index.html',
        page = 1,
        page_count = 1,
        setups=[],
        cars=[],
        tracks=[],
        search_params = search_params()
        )

