from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SelectMultipleField, BooleanField, SubmitField
from wtforms.fields import SelectFieldBase
from wtforms.validators import DataRequired
from .custom_fields import TagListField
from app.models import Tag


class WriteArticleForm(FlaskForm):
    title = StringField('', validators=[DataRequired()], render_kw={'placeholder': '标题'})
    body = TextAreaField('', validators=[DataRequired()])
    tags = SelectMultipleField('标签', coerce=int)
    disable_comment = BooleanField('是否禁止评论')  # 是否允许评论
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(WriteArticleForm, self).__init__(*args, **kwargs)
        choices = [(tag.id, tag.title) for tag in Tag.query.all()]
        self.tags.choices = choices


class EditArticleForm(FlaskForm):
    title = StringField('', validators=[DataRequired()], render_kw={'placeholder': '标题'})
    body = TextAreaField('', validators=[DataRequired()])
    tags = SelectMultipleField('标签', coerce=int)
    disable_comment = BooleanField('是否禁止评论')  # 是否允许评论
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(EditArticleForm, self).__init__(*args, **kwargs)
        choices = [(tag.id, tag.title) for tag in Tag.query.all()]
        self.tags.choices = choices
