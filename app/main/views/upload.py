import os

from PIL import Image
from flask import render_template, send_from_directory, current_app, url_for
from flask_login import login_required, current_user

from app import photos, db
from app.main import main
from app.main.forms import UploadForm
from app.main.views.search import search
from app.utils import image_resize


@main.route('/upload',methods=['GET','POST'])
@login_required
def upload_avatar():
    s = search()
    if s:
        return s
    form=UploadForm()
    if form.validate_on_submit():
        photoname=photos.save(form.photo.data)

        photo_url=photos.url(photoname)#原图
        avatar_url_sm=image_resize(photoname,30)
        avatar_url_nm=image_resize(photoname,400)
        current_user.avatar_url_sm=avatar_url_sm#缩略头像
        current_user.avatar_url_nm=avatar_url_nm#正常头像
        db.session.add(current_user)
    else:
        photo_url=None
    return render_template('index/upload.html',form=form,file_url=photo_url)


@main.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    # print(current_app.config['UPLOADED_PHOTOS_DEST'])
    return send_from_directory(current_app.config['UPLOADED_PHOTOS_DEST'],
                               filename)
