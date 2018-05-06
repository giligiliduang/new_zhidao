from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
from app.constants import types


class SearchForm(FlaskForm):
    type = SelectField('', coerce=int)
    content = StringField('', validators=[DataRequired(), Length(1, 30)], render_kw={'placeholder': '输入要搜索的内容'})
    submit = SubmitField('确定')

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        choices = self.generate_types()
        self.type.choices = choices

    def generate_types(self):
        res = []
        for each in enumerate(types, 0):
            res.append(each)
        return res
