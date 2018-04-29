from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import Length
from app.constants import jobs


class EditProfileForm(FlaskForm):
    name=StringField('姓名',validators=[Length(0,64)],render_kw={'placeholder':'姓名'})
    location=StringField('位置',validators=[Length(0,64)],render_kw={'placeholder':'所在地'})
    about_me=StringField('一句话介绍',validators=[Length(0,64)])#一句话
    job = SelectField('行业', coerce=int)  # 选择框
    submit=SubmitField('提交')
    def __init__(self,*args,**kwargs):
        super(EditProfileForm,self).__init__(*args,**kwargs)
        choices=self.generate_jobs()
        self.job.choices=choices
    def generate_jobs(self):
        res=[]
        for each in enumerate(jobs,0):
            res.append(each)
        return res