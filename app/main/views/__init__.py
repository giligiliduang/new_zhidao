
from flask import request, current_app, redirect, flash, url_for
from flask_sqlalchemy import get_debug_queries

from app.auth.forms import LoginForm
from app.models import Permission
from .. import main
from flask_login import current_user

from .answer import *
from .comment import *
from .favorite import *
from .index import *
from .post import *
from .question import *
from .upload import *
from .user import *
from .topic import *

__all__=['before_request','after_request','index','upload_avatar','image_resize',
         'user','user_answers','user_questions','user_posts','user_followed','user_followers',
         'unfollow_user','follow_user','my_followed_user_posts','my_followed_user_questions',
        'like_answer','unlike_answer','like_post','unlike_post','followed_favorites','followed_questions',

         'favorite','favorite_posts','favorite_questions','edit_favorite','create_favorite',
         'collect_post','collect_question','collect_answer',

         'edit_answer','write_answer','answer_comments',

         'post','post_order_by_likecount','post_order_by_timestamp','tag_posts','create_post','edit_post',
         'posts',
        'question','edit_question','pose_question','recent_questions','question_comments'
         ]

@main.before_app_request
def before_request():
    """请求钩子,拦截admin的请求
        没有权限或者未登录的重定向
    """
    if request.path.startswith('/admin'):
        if not current_user.is_authenticated:
            flash('请先登录')
            return redirect(url_for('auth.login'))
        else:
            if not current_user.can(Permission.ADMINISTER):
                flash('你不是管理员',category='warning')
                return redirect(url_for('main.index'))


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration>current_app.config['FLASK_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning('Slow query:{}\nParameters:{}\nDuration:{}\nContext:{}'\
                                       .format(query.statement,query.parameters,query.duration,query.context))
    return response
