from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField, SelectMultipleField
from wtforms.validators import Length
from app.models import Topic, Question


class QuestionForm(FlaskForm):
    title = StringField('', validators=[Length(0, 64)], render_kw={'placeholder': '标题'})
    description = TextAreaField('', validators=[Length(0, 100, message='100字以内')], render_kw={'placeholder': '描述'})
    topic = SelectMultipleField('话题', coerce=int)
    anonymous = BooleanField('匿名提问')
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        choices = [(topic.id, topic.title) for topic in Topic.query.order_by(Topic.timestamp.desc()).all()]
        self.topic.choices = choices

    def validate(self):
        checked = super(QuestionForm, self).validate()
        if not checked:
            return False
        question = Question.query.filter_by(title=self.title.data).first()
        if question:
            self.title.errors.append('您提问的问题已经存在,快去搜索一下吧')
            return False
        return True


class EditQuestionForm(FlaskForm):
    title = StringField('', validators=[Length(0, 64)], render_kw={'placeholder': '标题'})
    description = TextAreaField('', validators=[Length(0, 100, message='100字以内')], render_kw={'placeholder': '描述'})
    topic = SelectMultipleField('话题', coerce=int)
    anonymous = BooleanField('匿名提问')
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(EditQuestionForm, self).__init__(*args, **kwargs)
        choices = [(topic.id, topic.title) for topic in Topic.query.order_by(Topic.timestamp.desc()).all()]
        self.topic.choices = choices
        # def validate(self):
        #     checked=super(EditQuestionForm,self).validate()
        #     if not checked:
        #         return False
        #     question=Question.query.filter_by(title=self.title.data).first()
        #     if question:
        #         self.title.errors.append('您提问的问题已经存在,快去搜索一下吧')
        #         return False
        #     return True
