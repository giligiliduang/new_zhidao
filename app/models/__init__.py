from flask import flash, redirect, url_for, render_template, session
from flask_login import login_user

from app.site_admin.views import PostView, AnswerView, QuestionView, CommentView, CustomModelView, CustomFileAdmin, os
from .core import *
from .process_signals import *
from app import admin


__all__=[
    'PostTag','Tag','LikeAnswer','LikeComment','LikePost',
    'Post','Answer','Question','Topic','Favorite','QuestionTopic',
    'Follow','FollowFavorite','FollowQuestion','Comment',
    'User','Role','Permission'
]








views=[PostView(Post,db.session,category='数据库管理')
    ,AnswerView(Answer,db.session,category='数据库管理')
    ,QuestionView(Question,db.session,category='数据库管理')
    ,CommentView(Comment,db.session,category='数据库管理')
    ,CustomModelView(Topic,db.session,category='数据库管理')
    ,CustomModelView(User,db.session,category='数据库管理')
    ,CustomModelView(Role,db.session,category='数据库管理')
    ,CustomModelView(Favorite,db.session,category='数据库管理')
    ,CustomModelView(Tag,db.session,category='数据库管理')
    ,CustomFileAdmin(os.path.join(os.path.dirname(os.path.dirname(__file__)),'static'),name='文件管理')
    ]

admin.add_views(*views)
