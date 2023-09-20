from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from app import db, app
from models import Setup, Car, Track, SetupStat, SetupFile
from tools import JSONSaver
from sqlalchemy import update, delete
from flask_login import login_required, current_user
import bleach
from sqlalchemy import exc
import markdown
import os
import json

bp = Blueprint('setups', __name__, url_prefix='/setups')

PER_PAGE = 10

BMW_M4_DATA = {
    'wheel_rate':[90000, 120000, 144000],
    'bump_stop_up':[],
    'bump_stop_down':[],
    'max_bb':56,
    'max_toe':1,
    'max_camber':5,
    'preload':[20,40],
    'toe_min_front':-0.2,
    'toe_min_rear':0,
    'camber_min_front':-4,
    'camber_min_rear':-4,
    'caster_min':8,
    'min_bp':80,
    'min_bb':53,
    'max_steer_ration': 15
}

ASTON_MARTIN_V8_DATA = {
    'wheel_rate':[90000, 120000, 144000],
    'bump_stop_up':[],
    'bump_stop_down':[],
    'max_bb':56,
    'max_toe':1,
    'max_camber':5,
    'preload':[20,40],
    'toe_min_front':-0.1,
    'toe_min_rear':0,
    'camber_min_front':-4,
    'camber_min_rear':-4,
    'caster_min':8,
    'min_bp':80,
    'min_bb':53,
    'max_steer_ration': 15
}

STANDART_CAR_DATA = {
    'wheel_rate':[90000, 120000, 144000, 164000, 188000, 210000],
    'bump_stop_up':[100,200,300],
    'bump_stop_down':[100,200,300,400,500, 600,700],
    'max_bb':56,
    'max_toe':1,
    'max_camber':5,
    'preload':[20,40],
    'toe_min_front':-0.2,
    'toe_min_rear':0,
    'camber_min_front':-4,
    'camber_min_rear':-4,
    'caster_min':8,
    'min_bp':80,
    'min_bb':53,
    'max_steer_ration': 15
}

GENERAL_CAR_DATA = {
    'min_tire_pressure': 20.3,
    
}

CARS_DATA = {
    'BMW M4': BMW_M4_DATA,
    'Aston Martin V8': ASTON_MARTIN_V8_DATA,
    'Ferrari 296 GT3': STANDART_CAR_DATA,
    'Mercedes AMG GT3 EVO': STANDART_CAR_DATA,
    'Porsche 992 GT3 R': STANDART_CAR_DATA,
    'Audi R8 LMS GT3 EVO II': STANDART_CAR_DATA,
    'Mclaren 720S EVO': STANDART_CAR_DATA,
}
    

SETUP_PARAMS = [
    'time', 'description', 'car_id', 'track_id', 'condition_track', 'condition_air', 'title'
]

def user_is_author(setup):
    if setup.author_id == current_user.id:
        return True
    if current_user.is_admin():
        return True
    return False


def params():
    return { p: request.form.get(p) for p in SETUP_PARAMS }
    
@bp.route('/edit/<int:setupID>')
@login_required
def edit(setupID):
    try:
        setup = db.session.execute(db.select(Setup).filter_by(id=setupID)).scalar()
        
        if not user_is_author(setup):
            flash('Недостаточно прав для выполнения данного действия', 'warning')
            return redirect(url_for('index'))
        
        cars = db.session.execute(db.select(Car)).scalars()
        tracks = db.session.execute(db.select(Track)).scalars()
    except exc.SQLAlchemyError as error:
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
    
    return render_template('setups/edit_setup.html',setup=setup, cars=cars, tracks=tracks)
    
@bp.route('/edit_post/<int:setupID>', methods=['POST'])
@login_required
def edit_post(setupID):
    try:
        params_from_form = params()
        for param in params_from_form:
            param = bleach.clean(param)
            
        setup = Setup(**params_from_form)
        
        if not user_is_author(setup):
            flash('Недостаточно прав для выполнения данного действия', 'warning')
            return redirect(url_for('index'))
        
        db.session.query(Setup).filter(Setup.id == setupID).update({
            'time': setup.time_to_int(),
            'description': setup.description,
            'car_id': setup.car_id,
            'track_id': setup.track_id,
            'condition_air': setup.condition_air,
            'condition_track': setup.condition_track,
            'title': setup.title,
            })
        
        db.session.commit()
        
        flash('Запись успешно изменена','success')
        return redirect(url_for('setups.show', setupID = setupID))
        
    except exc.SQLAlchemyError as error:
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        db.session.rollback()
        return redirect(url_for('index'))

@bp.route('/create')
@login_required
def create():
    try:
        cars = db.session.execute(db.select(Car)).scalars()
        tracks = db.session.execute(db.select(Track)).scalars()
        return render_template('setups/add_setup.html',cars=cars, tracks=tracks)
    except:
        flash('Ошибка при загрузке данных', 'danger')
        return redirect(url_for('index'))
    
@bp.route('/delete/<int:setupID>', methods=['POST'])
@login_required
def delete_post(setupID):
#    try:
        setup = db.session.execute(db.select(Setup).filter_by(id = setupID)).scalar()
        if not user_is_author(setup):
            flash('Недостаточно прав для выполнения данного действия', 'warning')
            return redirect(url_for('index'))
        if Setup.query.filter_by(file_id=setup.file_id).count() == 1:
            file = db.session.execute(db.select(SetupFile).filter_by(id = setup.file_id)).scalar()
            os.remove(os.path.join(app.config['SETUPS_UPLOAD_FOLDER'], setup.file_id + '.json'))
            db.session.query(SetupFile).filter_by(id = setup.file_id).delete()

        db.session.query(Setup).filter_by(id = setupID).delete()
        db.session.query(SetupStat).filter_by(setup_id = setupID).delete()
    
        db.session.commit()
        flash('Запись успешно удалена', 'success')
        return redirect(url_for('user.profile'))
#    except:
 #       db.session.rollback()
  #      flash('Ошибка при удалении', 'danger')
   #     return redirect(url_for('index'))

@bp.route('/create_post', methods=['POST'])
@login_required
def create_post():
#    try:
        f = request.files.get('setup_file')
    
        if f and f.filename:
            setup_file = JSONSaver(f).save()
        if setup_file is None:
            flash('Проверьте файл (загружен не .json)')
            return redirect(url_for('index'))

        
        params_from_form = params()
        for param in params_from_form:
            param = bleach.clean(param)
            
        params_from_form['author_id'] = current_user.id
            
        setup = Setup(**params_from_form)
        setup.time = setup.time_to_int()
        if f:
            setup.file_id = setup_file.id
        db.session.add(setup)
        db.session.commit()
        flash(f'Настройка была успешно добавлена', 'success')
        return redirect(url_for('index'))
#    except:
 #       db.session.rollback()
  #      flash('Ошибка при добавлении','danger')
   #     return redirect(url_for('index'))
        
@bp.route('like/<int:setupID>')
def like(setupID):
    if current_user.check_already_action(setupID, app.config['SETUP_ACTIONS'].get('like', 2)):
        db.session.add(SetupStat(**{'user_id':current_user.id,'setup_id': setupID, 'action_id':app.config['SETUP_ACTIONS'].get('like', 2)}))
        db.session.commit()
    return redirect(url_for('setups.show', setupID=setupID))

@bp.route('/<int:setupID>')
def show(setupID):
    # try:
        setup = db.session.execute(db.select(Setup).filter_by(id=setupID)).scalar()
        setup.description = markdown.markdown(setup.description)
        
        with open(os.path.join(app.config['SETUPS_UPLOAD_FOLDER'], setup.file_id + '.json'), 'r', encoding='utf-8') as f: #открыли файл
            file = json.load(f)
        download_status = False
        if request.args.get('download_json'):
            download_status = True
        if download_status:
            path = f'media/files/{setup.file_id}.json'
            if current_user.is_authenticated:
                if current_user.check_already_action(setupID, app.config['SETUP_ACTIONS'].get('download', 1)):
                    db.session.add(SetupStat(**{'user_id':current_user.id,'setup_id': setup.id, 'action_id':app.config['SETUP_ACTIONS'].get('download', 1)}))
                    db.session.commit()
            return send_file(path, as_attachment=True, download_name=f'{setup.get_car()}_{setup.get_track()}_{setup.int_to_time}_{setup.condition_track}_{setup.condition_air}.json', mimetype="application/json")
        car_data = CARS_DATA.get(setup.get_car(), '')
        return render_template('setups/show_setup.html', setup=setup, file=file, car_data=car_data, general_car_data = GENERAL_CAR_DATA)
    # except:
    #     flash('Ошибка при отображении данных', 'danger')
    #     return redirect(url_for('index'))
        
