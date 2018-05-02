
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,BooleanField,PasswordField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, ValidationError
from ..models import User

class LoginForm(FlaskForm):
    email=StringField('',validators=[DataRequired(),Email(),Length(1,64)],render_kw={'placeholder':'邮箱'})
    password=PasswordField('',validators=[DataRequired(),Length(6,64)],render_kw={'placeholder':'密码'})
    remember_me=BooleanField('记住我')
    submit=SubmitField('登录')

    def validate(self):
        check_validate=super(LoginForm,self).validate()
        if not  check_validate:
            return False
        user=User.query.filter_by(email=self.email.data).first()#检验用户是否存在
        if user is None:
            self.email.errors.append('非法的用户名或密码')
            return False
        if not user.verify_password(self.password.data):
            self.password.errors.append('密码不正确')
            return False
        return True

class RegisterForm(FlaskForm):
    username=StringField('',validators=[DataRequired(),Length(max=255),Regexp('^[a-zA-Z][A-Za-z0-9_.]*$',0,'必须以数字字母下划线开头')],render_kw={'placeholder':'用户名'})
    email=StringField('',validators=[DataRequired(),Email(),Length(1,64)],render_kw={'placeholder':'邮箱'})
    password=PasswordField('',validators=[DataRequired(),EqualTo('password2',message='两次输入密码必须一致')],render_kw={'placeholder':'密码'})
    password2=PasswordField('',validators=[DataRequired()],render_kw={'placeholder':'确认密码'})
    submit=SubmitField('注册')
    def validate(self):
        check_validate=super(RegisterForm, self).validate()
        if not check_validate:
            return False
        username=User.query.filter_by(username=self.username.data).first()
        if username is not None:
            self.username.errors.append('用户名已经存在!')
            return False
        email=User.query.filter_by(email=self.email.data).first()
        if email is not None:
            self.email.errors.append('邮箱已经存在')
            return False
        return True

class ChangePasswordForm(FlaskForm):
    old_password=PasswordField('',validators=[DataRequired()],render_kw={'placeholder':'输入旧密码'})
    new_password=PasswordField('',validators=[DataRequired(),EqualTo('confirm_password')],render_kw={'placeholder':'输入新密码'})
    confirm_password=PasswordField('',validators=[DataRequired()],render_kw={'placeholder':'确认新密码'})
    submit=SubmitField('修改')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(message= '邮箱不能为空'), Length(1, 64),
                                             Email(message= '请输入有效的邮箱地址，比如：username@domain.com')],render_kw={'placeholder':'邮箱'})
    submit = SubmitField('重设密码')


class PasswordResetForm(FlaskForm):
    email = StringField('',validators=[DataRequired(message= '邮箱不能为空'), Length(1, 64),
                                             Email(message= '请输入有效的邮箱地址，比如：username@domain.com')],render_kw={'placeholder':'邮箱'})
    password = PasswordField('',validators=[
        DataRequired(message= u'密码不能为空'), EqualTo(u'password2', message=u'密码必须匹配。')],render_kw={'placeholder':'密码'})
    password2 = PasswordField('',validators=[DataRequired(message= u'密码不能为空')],render_kw={'placeholder':'确认密码'})
    submit = SubmitField('重设')

    def validate(self):
        check_validate=super(PasswordResetForm,self).validate()
        if not check_validate:
            return False
        user=User.query.filter_by(email=self.email.data).first()
        if user is None:
            self.email.errors.append('邮箱不存在')
            return False
        return True

class ChangeEmailForm(FlaskForm):
    email = StringField('新邮箱地址', validators=[DataRequired(message= '邮箱不能为空'), Length(1, 64),
                                                 Email(message= '请输入有效的邮箱地址，比如：username@domain.com')])
    password = PasswordField('密码', validators=[DataRequired(message= '密码不能为空')])
    submit = SubmitField('更新')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经注册过了，换一个吧。')
