from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import StringField, SubmitField, FileField, TextAreaField

from wtforms.validators import DataRequired,Length
from app.models import Topic
from app import photos


class CreateTopicForm(FlaskForm):
    title = StringField('', validators=[Length(0, 64)], render_kw={'placeholder': '标题'})
    description = TextAreaField('', validators=[Length(0, 100, message='100字以内')], render_kw={'placeholder': '描述'})
    photo = FileField(validators=[
        FileAllowed(photos, '只能上传图片！'),
        FileRequired('文件未选择！')])
    submit = SubmitField(u'上传')

    def validate(self):
        checked=super(CreateTopicForm,self).validate()
        if not checked:
            return False
        topic=Topic.query.filter_by(title=self.title.data).first()
        if topic:
            self.title.errors.append('话题已经存在了')
            return False
        return True


