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
from app.constants import MessageType,MessageStatus

@main.context_processor
def inject_permissions():
    searchform = SearchForm()
    return dict(Permission=Permission, searchform=searchform,MessageType=MessageType)  # 全局渲染表单


@main.app_template_global('choice')
def choice():
    styles = ['success', 'info', 'default', 'warning', 'danger', 'primary']
    return random.choice(styles)
@main.app_template_global('len')
def my_len(item):
    return len(item)

@main.add_app_template_filter
def replace_none(val):
    return '无' if not val else val

#发送邮件
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



#调整图片大小
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
    return url_for('main.uploaded_file', filename=filename + img_suffix[base_width] + ext, _external=True)

#生成验证码
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

_letter_cases = "abcdefghjkmnpqrstuvwxy"  # 小写字母，去除可能干扰的i，l，o，z
_upper_cases = _letter_cases.upper()  # 大写字母
_numbers = ''.join(map(str, range(3, 10)))  # 数字
init_chars = ''.join((_letter_cases, _upper_cases, _numbers))
fontType = "宋体.ttf"
font_path = 'C:/Windows/Fonts/simsun.ttc'

def create_validate_code(size=(120, 30),
                         chars=init_chars,
                         img_type="GIF",
                         mode="RGB",
                         bg_color=(255, 255, 255),
                         fg_color=(0, 0, 255),
                         font_size=18,
                         font_path=font_path,
                         length=4,
                         draw_lines=True,
                         n_line=(1, 2),
                         draw_points=True,
                         point_chance=2):
    '''
    @todo: 生成验证码图片
    @param size: 图片的大小，格式（宽，高），默认为(120, 30)
    @param chars: 允许的字符集合，格式字符串
    @param img_type: 图片保存的格式，默认为GIF，可选的为GIF，JPEG，TIFF，PNG
    @param mode: 图片模式，默认为RGB
    @param bg_color: 背景颜色，默认为白色
    @param fg_color: 前景色，验证码字符颜色，默认为蓝色#0000FF
    @param font_size: 验证码字体大小
    @param font_type: 验证码字体，默认为 Arial.ttf
    @param length: 验证码字符个数
    @param draw_lines: 是否划干扰线
    @param n_lines: 干扰线的条数范围，格式元组，默认为(1, 2)，只有draw_lines为True时有效
    @param draw_points: 是否画干扰点
    @param point_chance: 干扰点出现的概率，大小范围[0, 100]
    @return: [0]: PIL Image实例
    @return: [1]: 验证码图片中的字符串
    '''

    width, height = size  # 宽， 高
    img = Image.new(mode, size, bg_color)  # 创建图形
    draw = ImageDraw.Draw(img)  # 创建画笔
    if draw_lines:
        create_lines(draw, n_line, width, height)
    if draw_points:
        create_points(draw, point_chance, width, height)
    strs = create_strs(draw, chars, length, font_path, font_size, width, height, fg_color)

    # 图形扭曲参数
    params = [1 - float(random.randint(1, 2)) / 100,
              0,
              0,
              0,
              1 - float(random.randint(1, 10)) / 100,
              float(random.randint(1, 2)) / 500,
              0.001,
              float(random.randint(1, 2)) / 500
              ]
    img = img.transform(size, Image.PERSPECTIVE, params)  # 创建扭曲

    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)  # 滤镜，边界加强（阈值更大）

    return img, strs


def create_lines(draw, n_line, width, height):
    '''绘制干扰线'''
    line_num = random.randint(n_line[0], n_line[1])  # 干扰线条数
    for i in range(line_num):
        # 起始点
        begin = (random.randint(0, width), random.randint(0, height))
        # 结束点
        end = (random.randint(0, width), random.randint(0, height))
        draw.line([begin, end], fill=(0, 0, 0))


def create_points(draw, point_chance, width, height):
    '''绘制干扰点'''
    chance = min(100, max(0, int(point_chance)))  # 大小限制在[0, 100]

    for w in range(width):
        for h in range(height):
            tmp = random.randint(0, 100)
            if tmp > 100 - chance:
                draw.point((w, h), fill=(0, 0, 0))


def create_strs(draw, chars, length, font_path, font_size, width, height, fg_color):
    '''绘制验证码字符'''
    '''生成给定长度的字符串，返回列表格式'''
    c_chars = random.sample(chars, length)
    strs = ' %s ' % ' '.join(c_chars)  # 每个字符前后以空格隔开

    font = ImageFont.truetype(font_path, font_size)
    font_width, font_height = font.getsize(strs)

    draw.text(((width - font_width) / 3, (height - font_height) / 3), strs, font=font, fill=fg_color)

    return ''.join(c_chars)

#################################
#返回验证码数据流和字符
def generate_verification_code():
    code_img, str_text = create_validate_code()
    buf = BytesIO()
    code_img.save(buf, 'JPEG', quality=70)
    buf_str = buf.getvalue()
    return buf_str, str_text





