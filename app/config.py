import os

SECRET_KEY = 'os.urandom(10).hex()'

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://std_2033_assetto:Artem2558@std-mysql.ist.mospolytech.ru/std_2033_assetto'


SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

ADMIN_ROLE_ID = 1
MODER_ROLE_ID = 2
USER_ROLE_ID = 3

SETUP_ACTIONS = {
    'download': 1,
    'like': 2
}

MAX_CONTENT_LENGTH = 0.5 * 1024 * 1024

SETUPS_PER_PAGE_INDEX = 6
SETUPS_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'files')

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')

CAR_IMAGES = {
    'BMW M4':'m4_default.jpg',
    'Aston Martin V8': 'aston_martin_v8_default.jpg',
    'Ferrari 296 GT3': 'ferrari_296_default.jpg',
    'Mercedes AMG GT3 EVO': 'mercedes_amg_evo_default.jpg',
    'Porsche 992 GT3 R': 'porshe_992_r_default.jpg',
    'Audi R8 LMS GT3 EVO II': 'audi_r8_lms_evo_II.jpg',
    'Mclaren 720S EVO': 'mclaren_720s_gt3_evo.jpg',
    'Porsche 992 GT3 R': 'porsche_992__r.png'

}
