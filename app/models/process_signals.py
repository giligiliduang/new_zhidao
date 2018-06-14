from app import signals
from .core import *
from app.decorators import use_signal
from app import db
from flask_login import user_logged_in, user_logged_out
from datetime import datetime

"""
处理信号

"""


#############用户################

@use_signal(user_logged_in)
def update_user_lastseen(app, **kwargs):
    sender = kwargs.get('user')
    assert isinstance(sender, User)
    sender.lastseen = datetime.utcnow()
    db.session.add(sender)
    db.session.commit()





@use_signal(signals.user_visited)
def update_user_visited_count(sender):
    assert isinstance(sender, User)
    sender.visited += 1




###################回答#####################

@use_signal(signals.answer_comment_add)
@use_signal(signals.answer_comment_delete)
def update_answer_comment_count(sender):
    assert isinstance(sender, Answer)
    sender.comment_count = Answer.query.get(sender.id).comments.count()
    db.session.add(sender)
    db.session.commit()


@use_signal(signals.answer_voteup)
@use_signal(signals.answer_cancel_vote)
def update_answer_like_count(sender):
    assert isinstance(sender, Answer)
    sender.liked_count = Answer.query.get(sender.id).liked_answers.count()
    db.session.add(sender)
    db.session.commit()


################问题######################

@use_signal(signals.question_comment_add)
@use_signal(signals.question_comment_delete)
def update_question_comment_count(sender):
    assert isinstance(sender, Question)
    sender.comments_count = Question.query.get(sender.id).comments.filter(Comment.was_delete==False).count()
    db.session.add(sender)
    db.session.commit()


@use_signal(signals.question_answer_add)
def update_question_answer_count(sender):
    assert isinstance(sender, Question)
    sender.answers_count = Question.query.get(sender.id).answers.count()
    db.session.add(sender)
    db.session.commit()


@use_signal(signals.question_follow)
@use_signal(signals.question_unfollow)
def update_question_followers_count(sender):
    assert isinstance(sender, Question)
    sender.followers_count = Question.query.get(sender.id).followers.count()
    db.session.add(sender)
    db.session.commit()


@use_signal(signals.question_browsed)
def update_question_browsed_count(sender):
    assert isinstance(sender, Question)
    sender.browsed += 1
    print(sender.browsed)


####################文章###################

@use_signal(signals.post_comment_add)
@use_signal(signals.post_comment_delete)
def update_post_comment_count(sender):
    assert isinstance(sender, Post)
    sender.comments_count = Post.query.get(sender.id).comments.count()
    db.session.add(sender)
    db.session.commit()


@use_signal(signals.post_cancel_vote)
@use_signal(signals.post_voteup)
def update_post_like_count(sender):
    assert isinstance(sender, Post)
    sender.liked_count = Post.query.get(sender.id).liked_posts.count()
    db.session.add(sender)
    db.session.commit()


@use_signal(signals.post_tag_add)
def update_post_tag_count(sender):
    assert isinstance(sender, Post)
    sender.tag_count = Post.query.get(sender.id).tags.count()
    db.session.add(sender)
    db.session.commit()


##############收藏夹####################

@use_signal(signals.favorite_answer_add)
@use_signal(signals.favorite_answer_delete)
def update_favorite_answer_count(sender):
    assert isinstance(sender, Favorite)
    sender.answers_count = Favorite.query.get(sender.id).answers.count()
    db.session.add(sender)
    db.session.commit()


@use_signal(signals.favorite_comment_add)
@use_signal(signals.favorite_comment_delete)
def update_favorite_comment_count(sender):
    assert isinstance(sender, Favorite)
    sender.comments_count = Favorite.query.get(sender.id).comments.count()
    db.session.add(sender)
    db.session.commit()


@use_signal(signals.favorite_post_add)
@use_signal(signals.favorite_post_delete)
def update_favorite_post_count(sender):
    assert isinstance(sender, Favorite)
    sender.posts_count = Favorite.query.get(sender.id).posts.count()
    db.session.add(sender)
    db.session.commit()


@use_signal(signals.favorite_question_add)
@use_signal(signals.favorite_question_delete)
def update_favorite_question_count(sender):
    assert isinstance(sender, Favorite)
    sender.questions_count = Favorite.query.get(sender.id).questions.count()
    db.session.add(sender)
    db.session.commit()


@use_signal(signals.favorite_follow)
@use_signal(signals.favorite_unfollow)
def update_favorite_answer_count(sender):
    assert isinstance(sender, Favorite)
    sender.followers_count = Favorite.query.get(sender.id).followers.count()
    db.session.add(sender)
    db.session.commit()


############评论#################

@use_signal(signals.comment_voteup)
@use_signal(signals.comment_cancel_vote)
def update_comment_like_count(sender):
    assert isinstance(sender, Comment)
    sender.liked_count = Comment.query.get(sender.id).liked_comments.count()
    db.session.add(sender)
    db.session.commit()
@use_signal(signals.reply_cancel_vote)
@use_signal(signals.reply_voteup)
def update_reply_like_count(reply):
    reply.liked_count=Reply.query.get(reply.id).liked_replies.count()
    db.session.add(reply)
    db.session.commit()

############话题################

@use_signal(signals.topic_question_add)
@use_signal(signals.topic_question_delete)
def update_topic_question_count(sender):
    assert isinstance(sender, Topic)
    sender.questions_count = Topic.query.get(sender.id).questions.count()
    db.session.add(sender)
    db.session.commit()


@use_signal(signals.topic_follow)
@use_signal(signals.topic_unfollow)
def update_topic_followers_count(sender):
    assert isinstance(sender, Topic)
    sender.follower_count = Topic.query.get(sender.id).followers.count()
    db.session.add(sender)
    db.session.commit()

###########私信###############
