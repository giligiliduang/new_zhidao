from flask import url_for, request
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length


class FavoriteForm(FlaskForm):
    title = StringField('', validators=[DataRequired(), Length(1, 64)], render_kw={'placeholder': '标题'})  # 收藏夹的名称
    description = TextAreaField('描述', validators=[DataRequired()])
    public = BooleanField('是否公开')
    submit = SubmitField('提交')

    def validate(self):
        check_validate = super(FavoriteForm, self).validate()
        if not check_validate:
            return False
        favor = current_user.favorites.filter_by(title=self.title.data).first()
        if favor:
            edit_url = url_for('main.edit_favorite', username=favor.user.username, id=favor.id, _external=True)  # 编辑页面
            if edit_url == request.url:
                return True
            else:
                self.title.errors.append('收藏夹已经存在了')
                return False
        return True


class EditFavoriteForm(FlaskForm):
    title = StringField('', validators=[DataRequired(), Length(1, 64)], render_kw={'placeholder': '标题'})  # 收藏夹的名称
    description = TextAreaField('描述', validators=[DataRequired()])
    public = BooleanField('是否公开')
    submit = SubmitField('提交')

    def validate(self):
        check_validate = super(EditFavoriteForm, self).validate()
        if not check_validate:
            return False
        favor = current_user.favorites.filter_by(title=self.title.data).first()
        if favor:
            edit_url = url_for('main.edit_favorite', username=favor.user.username, id=favor.id, _external=True)  # 编辑页面
            if edit_url == request.url:
                return True
            else:
                self.title.errors.append('收藏夹已经存在了')
                return False
        return True


class CollectForm(FlaskForm):
    favorite = SelectField('选择收藏夹', coerce=int)
    submit = SubmitField('确定')

    def __init__(self, *args, **kwargs):
        super(CollectForm, self).__init__(*args, **kwargs)
        favorites = current_user.favorites.all()
        choices = [(favor.id, favor.title) for favor in favorites]
        self.favorite.choices = choices
