import os

from PIL import Image

from app.main import main
from app.main.forms import SearchForm
from app.models import Permission
import random

from threading import Thread
from flask import current_app, render_template, url_for
from flask_mail import Message
from app import mail, photos


@main.context_processor
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
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


img_suffix = {
    30: '_t',  # thumbnail
    400: '_s'  # show
}

def image_resize(image, base_width):
    #: create thumbnail
    filename, ext = os.path.splitext(image)
    img = Image.open(photos.path(image))
    if img.size[0] <= base_width:
        return photos.url(image)
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((base_width, h_size), Image.ANTIALIAS)
    img.save(os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], filename + img_suffix[base_width] + ext))
    return url_for('main.uploaded_file', filename=filename + img_suffix[base_width] + ext,_external=True)
