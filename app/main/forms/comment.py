from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    body = TextAreaField('', validators=[DataRequired()])  # 评论的内容
    submit = SubmitField('提交')

