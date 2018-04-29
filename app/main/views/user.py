from flask import flash, url_for, redirect, request, current_app, render_template, make_response
from flask_login import login_required, current_user

from app.decorators import permission_required
from app.main import main
from app.models import User, Question, Post, Answer, Permission, Follow, Favorite, FollowQuestion, FollowFavorite
from .search import search
from app.signals import user_visited, favorite_unfollow, \
    favorite_follow, question_unfollow, question_follow, post_voteup, post_cancel_vote, answer_cancel_vote, \
    answer_voteup

from app import signals

@main.route('/user/<username>',methods=['GET','POST'])
@login_required
def user(username):
    s = search()
    if s:
        return s
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('.index'))
    if user!=current_user:
        user_visited.send(user)
    page = request.args.get('page', 1, type=int)
    answers = None
    posts=None
    pagination = user.questions.order_by(Question.timestamp.desc()).paginate(
        page, per_page=current_app.config['ZHIDAO_QUESTION_PER_PAGE'], error_out=False
    )
    questions = pagination.items
    type = 'question'
    favorites=user.favorites.all()#全部收藏夹
    if request.cookies.get('items')=='1':
        #显示所有的答案
        pagination = user.answers.order_by(Answer.timestamp.desc()).paginate(
            page, per_page=current_app.config['ZHIDAO_QUESTION_PER_PAGE'], error_out=False
        )
        answers=pagination.items
        type='answer'
        a_context=dict( user=user,answers=answers, type=type,pagination=pagination,favorites=favorites)
        return render_template('user/personal.html',**a_context)
    elif request.cookies.get('items')=='3':
        pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['ZHIDAO_POST_PER_PAGE'], error_out=False
        )
        posts = pagination.items
        type = 'post'
        p_context=dict(user=user,posts=posts,type=type,pagination=pagination,favorites=favorites)
        return render_template('user/personal.html',**p_context)

    elif request.cookies.get('items')=='2':
        #默认显示所有提问
        pagination = user.questions.order_by(Question.timestamp.desc()).paginate(
            page, per_page=current_app.config['ZHIDAO_QUESTION_PER_PAGE'], error_out=False
        )
        questions = pagination.items
        type='question'
        q_context=dict(user=user, questions=questions,type=type,pagination=pagination,favorites=favorites)
        return render_template('user/personal.html',**q_context)

    return render_template('user/personal.html',user=user,questions=questions,answers=answers,posts=posts,type=type,pagination=pagination,favorites=favorites)

@main.route('/user/<username>/answers')
def user_answers(username):
    user=User.query.filter_by(username=username).first()
    if not user:
        flash('用户不存在')
        return redirect(url_for('.index'))
    resp=make_response(redirect(url_for('.user',username=user.username)))
    resp.set_cookie('items','1',max_age=24*60*60)
    return resp

@main.route('/user/<username>/questions')
def user_questions(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('用户不存在')
        return redirect(url_for('.index'))
    resp = make_response(redirect(url_for('.user', username=user.username)))
    resp.set_cookie('items', '2', max_age=24 * 60 * 60)
    return resp

@main.route('/user/<username>/posts')
def user_posts(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('用户不存在')
        return redirect(url_for('.index'))
    resp = make_response(redirect(url_for('.user', username=user.username)))
    resp.set_cookie('items', '3', max_age=24 * 60 * 60)
    return resp


@main.route('/follow/user/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow_user(username):
    """关注用户"""
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('.index'))
    if current_user.is_following_user(user):
        flash('你已经关注了该用户')
    current_user.follow(user)
    flash('关注了{}'.format(user.username))
    return redirect(url_for('.user',username=user.username))

@main.route('/unfollow/user/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow_user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('.index'))
    if user.is_followed_by_user(current_user):
        current_user.unfollow(user)
        flash('取消关注{}'.format(user.username))
        return redirect(url_for('.user',username=user.username))
    else:
        flash('你还没有关注该用户')



@main.route('/follow/favorite/<int:id>')
@login_required
@permission_required(Permission.FOLLOW)
def follow_favorite(id):
    favorite=Favorite.query.get_or_404(id)
    if favorite is None:
        flash('收藏夹不存在','warning')
        return redirect(url_for('.index'))
    if current_user.is_following_favorite(favorite):
        flash('你已经关注了收藏夹','info')
    current_user.follow(favorite)
    favorite_follow.send(favorite)
    flash('关注了收藏夹{}'.format(favorite.title),'info')
    return redirect(url_for('.favorite',username=favorite.user.username,id=favorite.id))

@main.route('/unfollow/favorite/<int:id>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow_favorite(id):
    favorite = Favorite.query.get_or_404(id)
    if favorite is None:
        flash('收藏夹不存在', 'warning')
        return redirect(url_for('.index'))
    if favorite.is_followed_by(current_user):
        current_user.unfollow(favorite)
        favorite_unfollow.send(favorite)
        flash('取消关注{}'.format(favorite.title),'info')
        return redirect(url_for('.favorite',username=favorite.user.username,id=favorite.id))
    else:
        flash('你还没有关注收藏夹')


@main.route('/follow/question/<int:id>')
@login_required
@permission_required(Permission.FOLLOW)
def follow_question(id):
    question=Question.query.get_or_404(id)
    if question is None:
        flash('问题不存在','warning')
        return redirect(url_for('.index'))
    if current_user.is_following_question(question):
        flash('你已经关注了问题','info')
    current_user.follow(question)
    question_follow.send(question)
    flash('关注了问题{}'.format(question.title),'info')
    return redirect(url_for('.question',id=question.id))

@main.route('/unfollow/question/<int:id>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow_question(id):
    question = Question.query.get_or_404(id)
    if question is None:
        flash('问题不存在','warning')
        return redirect(url_for('.index'))
    if question.is_followed_by(current_user):
        current_user.unfollow(question)
        question_unfollow.send(question)
        flash('取消关注了{}'.format(question.title),'info')
        return redirect(url_for('.question',id=question.id))
    else:
        flash('你还没有关注该问题','warning')





@main.route('/user/<username>/followers',methods=['GET','POST'])
def user_followers(username):
    """
    关注我的用户列表
    :param username:
    :return:
    """
    s = search()
    if s:
        return s
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('.index'))
    page=request.args.get('page',1,type=int)
    pagination=user.followers.order_by(Follow.timestamp.desc()).paginate(
        page,per_page=current_app.config['ZHIDAO_FOLLOW_PER_PAGE'],error_out=False
    )
    follows=[item.follower for item in pagination.items]#我的关注者
    style='user_followers'
    context=dict(follows=follows,user=user,
                           pagination=pagination,title='关注者',style=style)
    return render_template('user/user_follows.html',**context)

@main.route('/user/<username>/followed',methods=['GET','POST'])
def user_followed(username):
    """
    我关注的用户列表
    :param username:
    :return:
    """
    s = search()
    if s:
        return s
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('.index'))
    page=request.args.get('page',1,type=int)
    pagination=user.followed.order_by(Follow.timestamp.desc()).paginate(
        page,per_page=current_app.config['ZHIDAO_FOLLOW_PER_PAGE'],error_out=False
    )
    follows=[item.followed for item in pagination.items]#我关注的
    style='user_followed'
    context=dict(follows=follows,user=user,
                           pagination=pagination,title='关注的',style=style)
    return render_template('user/user_follows.html',**context)



@main.route('/user/<username>/followed-questions',methods=['GET','POST'])
def followed_questions(username):
    """
    我关注的问题
    :param username:
    :return:
    """
    s = search()
    if s:
        return s
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在','error')
        return redirect(url_for('.index'))
    page=request.args.get('page',1,type=int)
    pagination=user.followed_questions.order_by(FollowQuestion.timestamp.desc()).\
        paginate(page,per_page=current_app.config['ZHIDAO_FOLLOW_PER_PAGE'],error_out=False)
    follows=[item.followed for item in pagination.items]#关注的问题
    context=dict(questions=follows,user=user,pagination=pagination)
    return render_template('user/followed_questions.html',**context)

@main.route('/user/<username>/followed-favorites',methods=['GET','POST'])
def followed_favorites(username):
    """
    我关注的收藏夹
    :param username:
    :return:
    """
    s = search()
    if s:
        return s
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在', 'error')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed_favorites.order_by(FollowFavorite.timestamp.desc()). \
        paginate(page, per_page=current_app.config['ZHIDAO_FOLLOW_PER_PAGE'], error_out=False)
    follows = [item.followed for item in pagination.items]  # 关注的收藏夹
    context = dict(questions=follows, user=user, pagination=pagination)
    return render_template('user/followed_favorites.html',**context)

@main.route('/user/<username>/followed-user-questions')
def my_followed_user_questions(username):
    s = search()
    if s:
        return s
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('.index'))
    page=request.args.get('page',1,type=int)
    pagination=user.followed_user_questions.paginate(page,
    per_page=current_app.config['ZHIDAO_FOLLOW_PER_PAGE'],error_out=False)
    questions=pagination.items
    context=dict(questions=questions,user=user,pagination=pagination)
    return render_template('user/followed_user_questions',**context)

@main.route('/user/<username>/followed-user-posts')
def my_followed_user_posts(username):
    s = search()
    if s:
        return s
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed_user_posts.paginate(page,
                                                       per_page=current_app.config['ZHIDAO_FOLLOW_PER_PAGE'],
                                                       error_out=False)
    posts = pagination.items
    context = dict(posts=posts, user=user, pagination=pagination)
    return render_template('user/followed_user_posts', **context)



#点赞

@main.route('/like/post/<int:id>')
@login_required
@permission_required(Permission.FOLLOW)
def like_post(id):
    post=Post.query.get_or_404(id)
    if  current_user.is_like_post(post):
        flash('点过赞了','info')
    current_user.like(post)
    post_voteup.send(post)
    flash('点赞成功','success')
    return redirect(url_for('.post',id=post.id))

@main.route('/unlike/post/<int:id>')
@login_required
@permission_required(Permission.FOLLOW)
def unlike_post(id):
    post = Post.query.get_or_404(id)
    if post.is_liked_by(current_user):
        current_user.unlike(post)
        post_cancel_vote.send(post)
        flash('取消赞')
        return redirect(url_for('.post',id=post.id))
    flash('还没赞呢')

@main.route('/like/answer/<int:id>')
@login_required
@permission_required(Permission.FOLLOW)
def like_answer(id):
    answer=Answer.query.get_or_404(id)
    if current_user.is_like_answer(answer):
        flash('已经赞过了','info')
        return redirect(url_for('.question',id=answer.question_id))
    current_user.like(answer)
    answer_voteup.send(answer)
    flash('点赞成功','success')
    return redirect(url_for('.question',id=answer.question_id))

@main.route('/unlike/answer/<int:id>')
@login_required
@permission_required(Permission.FOLLOW)
def unlike_answer(id):
    answer=Answer.query.get_or_404(id)
    if answer.is_liked_by(current_user):
        current_user.unlike(answer)
        answer_cancel_vote.send(answer)
        flash('取消赞')
        return redirect(url_for('.question', id=answer.question_id))
    flash('还没赞呢')





