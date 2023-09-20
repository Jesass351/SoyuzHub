from flask import Blueprint, render_template, flash, redirect, url_for

bp = Blueprint('fuel', __name__, url_prefix='/setfuelups')


@bp.route('/')
def main():
    try:
        return render_template('fuel/fuel.html')
    except:
        flash('Ошибка при загрузке данных', 'danger')
        return redirect(url_for('index'))