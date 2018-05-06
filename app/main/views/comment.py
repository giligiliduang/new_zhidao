from flask import flash, redirect, url_for, abort, render_template
from flask_login import current_user, login_required

from app import db
from app.main import main
from app.main.forms import CommentForm
from app.models import Comment, Permission, Reply
from app.signals import question_comment_delete, answer_comment_delete, post_comment_delete


@main.route('/delete/comment/<int:id>')
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    if current_user == comment.author or current_user.can(Permission.MODERATE_COMMENTS):
        if comment.topic_type == 'question':
            q_id = comment.question.id
            question = comment.question
            db.session.delete(comment)
            db.session.commit()
            question_comment_delete.send(question)
            flash('删除评论成功', 'success')
            return redirect(url_for('.question_comments', id=q_id))
        elif comment.topic_type == 'post':

            p_id = comment.post.id
            post = comment.post
            db.session.delete(comment)
            db.session.commit()
            post_comment_delete.send(post)
            flash('删除评论成功', 'success')
            return redirect(url_for('.post', id=p_id))
        elif comment.topic_type == 'answer':
            a_id = comment.answer.id
            answer = comment.answer
            db.session.delete(comment)
            db.session.commit()
            answer_comment_delete.send(answer)
            flash('删除评论成功', 'success')
            return redirect(url_for('.answer_comments', id=a_id))
        return redirect(url_for('.index'))
    else:
        abort(403)


@main.route('/add_comment/comment/<int:id>', methods=['GET', 'POST'])
@login_required
def add_comment(id):
    """
    回复评论
    :param id:
    :return:
    """
    comment = Comment.query.get_or_404(id)
    form = CommentForm()
    topic_type = comment.topic_type
    if topic_type == 'post':
        return execute_comment(form, comment, 'post')
    elif topic_type == 'question':
        return execute_comment(form, comment, 'question')
    elif topic_type == 'answer':
        return execute_comment(form, comment, 'answer')
    elif topic_type == 'favorite':
        return execute_comment(form, comment, 'favorite')
    else:
        return execute_comment(form, comment, '')


def execute_comment(form, comment, topic_type):
    if comment.topic_type == topic_type and form.validate_on_submit():
        r = Reply.create(author=current_user._get_current_object(), body=form.body.data)
        comment.add_reply(r)
        return redirect(url_for('main.{}_comments'.format(topic_type), id=getattr(comment, topic_type).id))
    item = getattr(comment, topic_type)
    context = dict(form=form, item=item, comment=comment)
    return render_template('comment/add_comment.html', **context)


@main.route('/reply/reply/<int:id>/', methods=['GET', 'POST'])
@login_required
def reply(id):
    """
    回复评论里面的评论
    :param id:
    :return:
    """
    reply = Reply.query.get_or_404(id)  # 当前回复
    comment = reply.comment

    user = reply.author  # 我要回复的人
    replies = comment.replies.filter(db.or_(db.and_(Reply.author == current_user, Reply.user == user),
                                            db.and_(Reply.author == user, Reply.user == current_user))).all()

    form = CommentForm()

    if comment.topic_type == 'post':
        return execute_reply(comment, form=form, user=user, topic_type='post', replies=replies)
    elif comment.topic_type == 'question':
        return execute_reply(comment, form=form, user=user, topic_type='question', replies=replies)
    elif comment.topic_type == 'answer':
        return execute_reply(comment, form=form, user=user, topic_type='answer', replies=replies)
    elif comment.topic_type == 'favorite':
        return execute_reply(comment, form=form, user=user, topic_type='favorite', replies=replies)

    else:
        return execute_reply(comment=comment, form=form, user=user, topic_type='', replies=replies)


def execute_reply(comment, form, user, topic_type, **kwargs):
    if comment.topic_type == topic_type and form.validate_on_submit():
        r = Reply.create(author=current_user._get_current_object(), body=form.body.data, user=user)
        comment.add_reply(r)
        if topic_type == 'post':
            return redirect(url_for('main.{}'.format(topic_type), id=getattr(comment, topic_type).id))
        return redirect(url_for('main.{}_comments'.format(topic_type), id=getattr(comment, topic_type).id))

    replies = kwargs.get('replies')
    print(replies)
    context = dict(form=form, user=user, replies=replies, comment=comment)
    return render_template('comment/reply.html', **context)
