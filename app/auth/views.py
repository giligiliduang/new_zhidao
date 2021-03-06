from .forms import LoginForm, RegisterForm, ChangePasswordForm, PasswordResetForm, PasswordResetRequestForm, \
    ChangeEmailForm
from . import auth
from ..models import User, db
from flask_login import login_user, logout_user, login_required, current_user,fresh_login_required
from flask import redirect, url_for, render_template, flash, request, session, make_response
from ..utils import send_email,generate_verification_code



@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate() and request.method == 'POST':
        user = User.query.filter_by(email=form.email.data).first()
        if user.verify_password(password=form.password.data):
            if 'code_text' in session and form.verification_code.data==session['code_text']:
                login_user(user, remember=form.remember_me.data)  # 是否记住登录状态
                flash('登录成功', category='success')
                session.pop('code_text')
                return redirect(url_for('main.index') or request.args.get('next'))
            else:
                flash('验证码错误{}'.format(form.verification_code.data))
                return redirect(url_for('auth.login'))
        else:
            flash('密码错误')
    return render_template('security/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('退出登录', category='info')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if 'code_text' in session and session['code_text'] != form.verification_code.data:
            flash('输入错误：%s' % form.verification_code.data,'error')
            return redirect(url_for('auth.register'))
        else:
            flash('输入验证码正确','success')
            session.pop('code_text')
            user = User.create(email=form.email.data, username=form.username.data, password=form.password.data)
            token = user.generate_confirm_token()
            send_email(user.email, '确认账户', 'security/email/confirm', user=user, token=token)
            flash('注册成功', category='success')
            return redirect(url_for('auth.login'))
    return render_template('security/register.html', form=form)


@auth.route('/confirm.txt/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('验证通过，谢谢', category='success')
        return redirect(url_for('auth.login'))
    else:
        flash('令牌过期或令牌非法', category='error')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
            flash('你还没有通过认证')
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('security/unconfirmed.html')


@auth.route('/resend_confirmation')
def resend_confirmation():
    token = current_user.generate_confirm_token()
    send_email(current_user.email, '确认账户', 'security/email/confirm', user=current_user, token=token)
    flash('新的确认邮件已经发送', category='info')
    return redirect(url_for('main.index'))


@auth.route('/change_password', methods=['GET', 'POST'])
@fresh_login_required
def change_password():
    """更改密码"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            flash('密码修改成功', category='success')
            return redirect(url_for('main.index'))
        else:
            flash('输入的密码不正确', category='warning')
    return render_template('security/change_password.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = current_user.generate_reset_token()
            send_email(form.email.data, '重置密码', 'security/email/reset_password', user=user, token=token,
                       next=request.args.get('next'))
            flash('重置密码邮件已经发送', category='info')
            return redirect(url_for('auth.login'))
    return render_template('security/reset_password.html', form=form)


@auth.route('/reset/<token>')
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('密码重置成功')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('security/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@fresh_login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, u'确认你的邮箱地址',
                       'security/email/change_email',
                       user=current_user, token=token)
            flash('一封确认邮件已经发送到你的新邮箱，请及时查收。', 'info')
            return redirect(url_for('main.index'))
        else:
            flash('邮箱地址或密码无效。', 'warning')
    return render_template("security/change_email.html", form=form)


@auth.route('/change-email/<token>')
@fresh_login_required
def change_email(token):
    if current_user.change_email(token):
        flash('你的邮箱地址已经更新。', 'success')
    else:
        flash('请求无效.', 'warning')
    return redirect(url_for('main.index'))

@auth.route('/verifyCode/')
def get_verify_code():
    code_img, code_text = generate_verification_code()
    session['code_text'] = code_text
    response = make_response(code_img)
    response.headers['Content-Type'] = 'image/jpeg'
    return response