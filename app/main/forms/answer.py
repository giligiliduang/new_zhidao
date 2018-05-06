from flask_wtf import FlaskForm
from wtforms import TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class WriteAnswerForm(FlaskForm):
    body = TextAreaField('回答', validators=[DataRequired(message='内容不能为空')])
    anonymous = BooleanField('匿名回答')
    submit = SubmitField('提交')


class EditAnswerForm(FlaskForm):
    body = TextAreaField('回答', validators=[DataRequired(message='内容不能为空')])
    anonymous = BooleanField('匿名回答')
    submit = SubmitField('提交')
