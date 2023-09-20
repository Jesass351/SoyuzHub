import hashlib
import uuid
import os
from werkzeug.utils import secure_filename
from models import Image, SetupFile, Setup
from app import db, app

def filtered_setups(search_params): #фу
    query = db.select(Setup)
    if search_params.get('car_id') and search_params.get('car_id') != 'default':
        query = query.filter_by(car_id = search_params.get('car_id'))
    if search_params.get('track_id') and search_params.get('track_id') != 'default':
        query = query.filter_by(track_id = search_params.get('track_id'))
        
    return query
    
class JSONSaver:
    def __init__(self, file):
        self.file = file

    def save(self):        
        self.json = self.__find_by_md5_hash()
        if self.json is not None:
            return self.json
        file_name = secure_filename(self.file.filename)
        new_id = str(uuid.uuid4())
        file_name = new_id + os.path.splitext(file_name)[1]
        self.json = SetupFile(
            id = new_id,
            file_name = file_name,
            MIME = self.file.mimetype,
            MD5 = self.MD5)
        if self.json.MIME == 'application/json':
            self.file.save(
                os.path.join(app.config['SETUPS_UPLOAD_FOLDER'],
                            self.json.storage_filename))
            db.session.add(self.json)
            db.session.commit()
            return self.json
        else:
            return None

    def __find_by_md5_hash(self):
        self.MD5 = hashlib.md5(self.file.read()).hexdigest()
        self.file.seek(0)
        return db.session.execute(db.select(Image).filter(Image.MD5 == self.MD5)).scalar()
