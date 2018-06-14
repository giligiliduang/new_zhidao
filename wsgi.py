import forgery_py
from faker import Faker,Factory
from flask import Request
from app import create_app, db
from app.models import *
from flask_migrate import Migrate
import pymysql
import click
from click import prompt
from app import signals
from app.constants import MessageType,MessageStatus
app = create_app('development')
migrate = Migrate(app, db)
pymysql.install_as_MySQLdb()
fake=Factory.create()

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Question=Question, Answer=Answer,
                Topic=Topic, PostTag=PostTag, Post=Post, Tag=Tag, Comment=Comment,
                Favorite=Favorite, LikePost=LikePost, LikeAnswer=LikeAnswer, LikeComment=LikeComment,
                LikeReply=LikeReply, Follow=Follow, QuestionTopic=QuestionTopic, Reply=Reply, Message=Message,
                MessageType=MessageType,MessageStatus=MessageStatus)


@app.cli.command()
def test():
    """Run the unit tests"""
    import unittest
    tests = unittest.TestLoader().discover('tests',pattern='test_comment_model.py')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
def init_db():
    """
    初始化数据库，生成文章标签和话题
    """
    db.drop_all()
    db.create_all()
    click.echo(click.style('数据库初始化成功', fg='green'))
    Tag.generate_tags()
    click.echo('生成标签成功')
    Topic.generate_topics()
    click.echo('生成话题成功')

@app.cli.command()
def drop_db():
    """
    删除数据库数据
    """
    rv = prompt('是否删除数据库?', confirmation_prompt=True)
    if rv:
        db.drop_all()
        click.echo(click.style('数据库删除成功', fg='green'))


@app.cli.command()
def create_superadmin():
    """
    创建管理员账户
    """
    import re
    PWD_PATTERN = re.compile(r'^[a-zA-Z\d_]{8,}$')  # 长度8位
    EMAIL_PATTERN = re.compile(r'^[A-Za-zd0-9]+([-_.][A-Za-zd]+)*@([A-Za-zd0-9]+[-.])+[A-Za-zd]{2,5}$')
    password_passed = False
    email_passed = False
    while not email_passed:
        email = prompt('请输入邮箱')
        if EMAIL_PATTERN.match(email):
            email_passed = True
        else:
            click.echo('邮箱格式错误,请重新输入', color='red')
    username = prompt('请输入用户名')
    while not password_passed:
        pwd = prompt('请输入密码', hide_input=True)
        pwd1 = prompt('再输入一遍', hide_input=True)
        if PWD_PATTERN.match(pwd) and PWD_PATTERN.match(pwd1):
            password_passed = True
        if not password_passed:
            click.echo(click.style('验证未通过，请重新输入', fg='red'))

    if pwd == pwd1:
        u = User.query.filter_by(username=username).first()
        if u:
            click.echo(click.style('用户已经存在!', fg='red'))
            return
        u = User.create(username=username, password=pwd, confirmed=True, email=email)
        u.role = Role.query.filter_by(name='Administrator').first()
        db.session.add(u)
        db.session.commit()
        click.echo(click.style('创建成功', fg='green'))
        return
    click.echo(click.style('两次输入的密码不一致', fg='red'))
    return


@app.cli.command()
def drop_superadmin():
    """删除管理员账户 """
    name = prompt('请输入要删除的管理员用户名')
    admin = Role.query.filter_by(name='Administrator').first()
    u = User.query.filter(User.username == name, User.role == admin).first()
    if u:
        rv = prompt('确定删除管理员?', confirmation_prompt=True)
        if rv:
            db.session.delete(u)
            db.session.commit()
            click.echo(click.style('删除成功', fg='green'))
            return
    click.echo(click.style('要删除的用户不存在！', fg='red'))


@app.cli.command()
@click.argument('name')
def create_newapp(name):
    """
    创建新应用
    """
    import os
    BASE_DIR = os.path.dirname(__file__)
    app_dir = os.path.join(BASE_DIR, name)
    os.mkdir(app_dir)
    files = ['__init__.py', 'views.py', 'forms.py', 'errors.py']
    with click.progressbar(files, label='创建中...') as bar:
        for each in bar:
            try:
                each_file = os.path.join(app_dir, each)
                with open(each_file, 'w') as f:
                    pass
            except FileExistsError as e:
                print(e)
                break


@app.cli.command()
@click.argument('numbers',default=50)
def generate_fake_users(numbers):
    """
    生成假用户并让他们随机关注话题
    """
    import random

    with click.progressbar(range(int(numbers)), label='正在生成 用户 数据') as bar:
        for i in bar:
            username = forgery_py.internet.user_name()
            email = forgery_py.internet.email_address()
            password = '123456'
            location = forgery_py.address.city()
            job = forgery_py.name.job_title()
            about_me = 'Have a nice day'
            User.create(username=username, email=email, password=password, location=location,
                        job=job, about_me=about_me, confirm=True)
    users = User.query.all()[1:]
    topics = Topic.query.all()
    with click.progressbar(users, label='随机关注话题')as bar:
        for each_user in bar:
            chosen_topics = random.sample(topics, 4)
            for i in chosen_topics:
                each_user.follow(i)
                signals.topic_follow.send(i)


@app.cli.command()
@click.argument('numbers',default=50)
def generate_fake_questions(numbers):
    """
    生成假问题
    """
    import random
    users = User.query.all()
    with click.progressbar(range(int(numbers)), label='正在生成 问题 数据', fill_char='*') as bar:
        for i in bar:
            title = forgery_py.lorem_ipsum.title()
            description = 'HELP ME PLEASE'
            author = random.choice(users)
            Question.create(title=title, description=description, author=author)


@app.cli.command()
@click.argument('numbers',default=50)
def generate_fake_posts(numbers):
    """
    生成假文章

    """
    import random
    users = User.query.all()
    tags = Tag.query.all()
    with click.progressbar(range(int(numbers)), label='正在文章生成数据', fill_char='*') as bar:
        for i in bar:
            title = fake.sentence()[:15]
            body = fake.text()
            author = random.choice(users)
            tag = random.sample(tags, 2)
            p = Post.create(title=title, body=body, author=author)
            for each in tag:
                each.add_post(p)
                signals.post_tag_add.send(p)


@app.cli.command()
def random_topic_follow():
    """
    随机关注,用户，话题
    """
    import random
    users = User.query.all()[1:]
    topics = Topic.query.all()
    with click.progressbar(users, label='随机关注话题中') as bar:
        for each_user in bar:
            for i in random.sample(topics, 10):
                each_user.follow(i)
                signals.topic_follow.send(i)


@app.cli.command()
def random_topic_question_add():
    """
    给话题随机添加问题
    """
    import random
    questions = Question.query.all()
    topics = Topic.query.all()
    with click.progressbar(topics, label='添加问题中', fill_char='*') as bar:
        for each_topic in bar:
            for i in random.sample(questions, 5):
                each_topic.add_question(i)
                signals.topic_question_add.send(each_topic)

@app.cli.command()
def init_data_for_website():
    """
    生成基础数据
    :return:
    """
    import os
    os.system('set FLASK_APP=wsgi.py')#设置环境变量
    os.system('flask drop_db')#删除数据库
    os.system('flask init_db')#初始化数据库
    os.system('flask generate_fake_users')#生成用户数据
    os.system('flask generate_fake_questions')#生成问题数据
    os.system('flask generate_fake_posts 2')#生成文章数据
    os.system('flask random_topic_question_add')#给话题随机添加问题



if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run(host='localhost', port=5001, debug=True)




