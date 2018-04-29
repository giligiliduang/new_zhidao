
from app import create_app,db
from app.models import *
from flask_migrate import Migrate
import pymysql
import click
from click import prompt
app=create_app('development')
migrate=Migrate(app,db)
pymysql.install_as_MySQLdb()

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Question=Question, Answer=Answer,
                Topic=Topic, PostTag=PostTag, Post=Post, Tag=Tag, Comment=Comment,
                Favorite=Favorite, LikePost=LikePost, LikeAnswer=LikeAnswer, LikeComment=LikeComment,
                Follow=Follow,)


@app.cli.command()
def test():
    """Run the unit tests"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
def init_db():
    """
    initialize the database
    """
    db.drop_all()
    db.create_all()
    click.echo(click.style('数据库初始化成功', fg='green'))
@app.cli.command()
def drop_db():
    """
    drop db from env
    """
    rv=prompt('是否删除数据库?',confirmation_prompt=True)
    if rv:
        db.drop_all()
        click.echo(click.style('数据库删除成功', fg='green'))
@app.cli.command()
def create_superadmin():
    """
    create superadmin for the website
    """
    import re
    PWD_PATTERN=re.compile(r'^[a-zA-Z\d_]{8,}$')#长度8位
    passed=False
    username=prompt('请输入用户名')
    while not passed:
        pwd=prompt('请输入密码',hide_input=True)
        pwd1=prompt('再输入一遍',hide_input=True)
        if PWD_PATTERN.match(pwd) and PWD_PATTERN.match(pwd1):
            passed=True
        if not passed:
            click.echo(click.style('验证未通过，请重新输入', fg='red'))

    if pwd==pwd1:
        u=User.query.filter_by(username=username).first()
        if u:
            click.echo(click.style('用户已经存在!', fg='red'))
            return
        u=User(username=username,password=pwd,confirmed=True)
        u.role=Role.query.filter_by(name='Administrator').first()
        db.session.add(u)
        db.session.commit()
        click.echo(click.style('创建成功', fg='green'))
        return
    click.echo(click.style('两次输入的密码不一致', fg='red'))
    return

@app.cli.command()
def drop_superadmin():
    """drop superadmin """
    name=prompt('请输入要删除的管理员用户名')
    admin=Role.query.filter_by(name='Administrator').first()
    u=User.query.filter(User.username==name,User.role==admin).first()
    if u:
        rv=prompt('确定删除管理员?',confirmation_prompt=True)
        if rv:
            db.session.delete(u)
            db.session.commit()
            click.echo(click.style('删除成功',fg='green'))
            return
    click.echo(click.style('要删除的用户不存在！',fg='red'))

@app.cli.command()
@click.argument('name')
def create_newapp(name):
    import os
    BASE_DIR=os.path.dirname(__file__)
    app_dir=os.path.join(BASE_DIR,name)
    os.mkdir(app_dir)
    files=['__init__.py','views.py','forms.py','errors.py']
    with click.progressbar(files,label='创建中...') as bar:
        for each in bar:
            try:
                each_file=os.path.join(app_dir,each)
                with open(each_file,'w') as f:
                    pass
            except FileExistsError as e:
                print(e)
                break



if __name__ == '__main__':
    app.run()
