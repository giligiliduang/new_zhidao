from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from wtforms.widgets import TextArea


class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


class AdminLoginForm(FlaskForm):
    email = StringField('', validators=[DataRequired(), Email(), Length(1, 64)], render_kw={'placeholder': '邮箱'})
    password = PasswordField('', validators=[DataRequired(), Length(6, 64)], render_kw={'placeholder': '密码'})
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')
