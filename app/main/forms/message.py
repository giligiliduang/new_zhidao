from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired
from app.models import User

class MessageForm(FlaskForm):
    body = TextAreaField('', validators=[DataRequired()])  #私信的内容
    submit = SubmitField('提交')

class SendMessageForm(FlaskForm):



    user = QuerySelectField( validators=[DataRequired()],
                            query_factory=lambda :User.query.filter(User.id!=current_user.id),
                            get_pk=lambda x:x.id,get_label=lambda x:x.username)
    body = TextAreaField('', validators=[DataRequired()])  # 私信的内容
    submit=SubmitField('提交')

