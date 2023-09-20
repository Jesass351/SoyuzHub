from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from app import db, app
from models import User, Setup, SetupStat
from tools import JSONSaver
from sqlalchemy import update, delete
from flask_login import login_required, current_user
import bleach
from sqlalchemy import exc
from auth import check_rights
import markdown
import os
import json

bp = Blueprint('user', __name__, url_prefix='/user')

USER_PARAMS = [
    'time', 'description', 'car_id', 'track_id', 'condition_track', 'condition_air', 'title'
]

def params():
    return { p: request.form.get(p) for p in USER_PARAMS }

@bp.route('profile')
@login_required
def profile():
    setups = db.session.execute(db.select(Setup).filter_by(author_id=current_user.id)).scalars()
    return render_template('user/profile.html', setups=setups)
        
