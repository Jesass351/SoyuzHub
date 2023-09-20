import os
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from flask import url_for,  current_app
from app import db, app
from users_policy import UsersPolicy

class Roles(db.Model):
    __tablename__ = 'Roles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return '<Role %r>' % self.title
    
    
class User(db.Model, UserMixin):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    login = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role_id = db.Column(db.Integer, default=3)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, action, record=None):
        users_policy = UsersPolicy(record)
        method = getattr(users_policy, action, None)
        if method:
            return method()
        return False

    @property
    def full_name(self):
        return ' '.join([self.last_name, self.first_name, self.middle_name or ''])

    def __repr__(self):
        return '<User %r>' % self.login
    
    def is_admin(self):
        return self.role_id == current_app.config["ADMIN_ROLE_ID"]
    
    def is_moder(self):
        return self.role_id == current_app.config["MODER_ROLE_ID"]
    
    def is_user(self):
        return self.role_id == current_app.config["USER_ROLE_ID"]
    
    def check_already_action(self, setup, action):
        return db.session.execute(db.select(SetupStat).filter_by(user_id=self.id, setup_id=setup, action_id=action)).scalar() == None
        
class Setup(db.Model):
    __tablename__ = 'Setups'
    
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('Cars.id'), nullable=False)
    track_id = db.Column(db.Integer, db.ForeignKey('Tracks.id'), nullable=False)
    condition_track = db.Column(db.Integer, nullable=False)
    condition_air = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    author_id = db.Column(db.Integer, nullable=False)
    file_id = db.Column(db.String(40), nullable=False)
    
    downloaded = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, nullable=False, server_default=sa.sql.func.now())
    
    car = db.relationship('Car')
    track = db.relationship('Track')
    
    
    def get_car(self, img_name = False):
        car = db.session.execute(db.select(Car).filter_by(id=self.car_id)).scalar()
        car_img_name = None
        if img_name:
            car_img_name = 'images/' + app.config['CAR_IMAGES'].get(car.name, '')
            return car.name, car_img_name
        return car.name
    
    def get_track(self):
        return db.session.execute(db.select(Track).filter_by(id=self.track_id)).scalar().name
    
    def get_author_login(self):
        return db.session.execute(db.select(User).filter_by(id=self.author_id)).scalar().login
    
    def get_action_count(self, action):
        return SetupStat.query.filter_by(setup_id=self.id, action_id=action).count()
    
    def time_to_int(self):
        time = self.time.split(':')
        minutes = int(time[0]) * 60
        secs = float(time[1])
        return minutes + secs
    
    @property
    def int_to_time(self):
        minutes = int(self.time // 60)
        secs = round(self.time - minutes * 60, 1)
        return f'{minutes}:{secs}'
    
class SetupStat(db.Model):
    __tablename__ = 'SetupStat'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    setup_id = db.Column(db.Integer, nullable=False)
    action_id = db.Column(db.Integer, nullable=False)

class Car(db.Model):
    __tablename__ = 'Cars'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
class Track(db.Model):
    __tablename__ = 'Tracks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Image(db.Model):
    __tablename__ = 'Images'

    id = db.Column(db.String(150), primary_key=True)
    file_name = db.Column(db.String(250), nullable=False)
    MIME = db.Column(db.String(250), nullable=False)
    MD5 = db.Column(db.String(150), nullable=False)
    

    def __repr__(self):
        return '<Image %r>' % self.file_name

    @property
    def storage_filename(self):
        _, ext = os.path.splitext(self.file_name)
        return self.id + ext

    @property
    def url(self):
        return url_for('image', image_id=self.id)
    
class SetupFile(db.Model):
    __tablename__ = 'SetupFiles'

    id = db.Column(db.String(150), primary_key=True)
    file_name = db.Column(db.String(250), nullable=False)
    MIME = db.Column(db.String(250), nullable=False)
    MD5 = db.Column(db.String(150), nullable=False)
    

    def __repr__(self):
        return '<Image %r>' % self.file_name

    @property
    def storage_filename(self):
        _, ext = os.path.splitext(self.file_name)
        return self.id + ext

    @property
    def url(self):
        return url_for('image', image_id=self.id)
    
    @property
    def ext(self):
        return os.path.splitext(self.file_name)[1]
        
