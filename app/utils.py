from app.main import main
from app.main.forms import SearchForm
from app.models import Permission
import random

from multiprocessing import Process
from flask import current_app, render_template
from flask_mail import Message
from app import mail


@main.app_context_processor
def inject_permissions():
    searchform=SearchForm()
    return dict(Permission=Permission,searchform=searchform)#全局渲染表单
@main.app_template_global('choice')
def choice():
    styles = ['success', 'info', 'default', 'warning', 'danger', 'primary']
    return random.choice(styles)


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['ZHIDAO_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['ZHIDAO_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Process(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

