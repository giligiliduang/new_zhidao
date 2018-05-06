from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import FileField, SubmitField

from app import photos


class UploadForm(FlaskForm):
    photo = FileField(validators=[
        FileAllowed(photos, '只能上传图片！'),
        FileRequired('文件未选择！')])
    submit = SubmitField(u'上传')
