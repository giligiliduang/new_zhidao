from flask import flash, redirect, url_for, abort,render_template
from flask_login import current_user, login_required

from app import db
from app.main import main
from app.main.forms import CommentForm
from app.models import Comment, Permission
from app.signals import question_comment_delete,answer_comment_delete,post_comment_delete

@main.route('/delete/comment/<int:id>')
def delete_comment(id):
    comment=Comment.query.get_or_404(id)
    if current_user==comment.author or current_user.can(Permission.MODERATE_COMMENTS):
        if comment.topic_type=='question':
            q_id=comment.question.id
            question=comment.question
            db.session.delete(comment)
            db.session.commit()
            question_comment_delete.send(question)
            flash('删除评论成功','success')
            return redirect(url_for('.question_comments',id=q_id))
        elif comment.topic_type=='post':

            p_id=comment.post.id
            post=comment.post
            db.session.delete(comment)
            db.session.commit()
            post_comment_delete.send(post)
            flash('删除评论成功','success')
            return redirect(url_for('.post',id=p_id))
        elif comment.topic_type=='answer':
            a_id=comment.answer.id
            answer=comment.answer
            db.session.delete(comment)
            db.session.commit()
            answer_comment_delete.send(answer)
            flash('删除评论成功', 'success')
            return redirect(url_for('.answer_comments',id=a_id))
        return redirect(url_for('.index'))
    else:
        abort(403)




@main.route('/reply/comment/<int:id>/')
@login_required
def reply(id):
    comment=Comment.query.get_or_404(id)#获取评论
    form=CommentForm()
    user=comment.author
    # if current_user == user:
    #     flash('自己不能回复自己')
    #     return redirect(url_for('.index',username=current_user.username))
    if comment.topic_type=='post':
        if form.validate_on_submit():
            comment = Comment.create(author=current_user._get_current_object(), user=user,
                              topic_type='post_reply', body=form.body.data,post=comment.post)  # 被回复的是作者
            db.session.add(comment)
            db.session.commit()
            flash('回复成功', category='success')
            return redirect(url_for('.reply', id=comment.id))
        post=comment.post
        comments=user.comments.filter_by(topic_type='post').order_by(Comment.timestamp.desc()).all()
        replies=user.comments_from.filter_by(topic_type='post_reply').order_by(Comment.timestamp.desc()).all()#在文章中的回复
        total=comments+replies
        print(total)
        return render_template('post/post.html',form=form,replies=replies,post=post,comments=total)#评论和回复
    elif comment.topic_type=='question':
        if form.validate_on_submit():
            comment = Comment.create(author=current_user._get_current_object(), user=user,
                              topic_type='question_reply', body=form.body.data,question=comment.question)  # 被回复的是作者
            db.session.add(comment)
            db.session.commit()
            flash('回复成功', category='success')
            return redirect(url_for('.reply', id=comment.id))
        question = comment.question
        comments = user.comments.filter_by(topic_type='question').order_by(Comment.timestamp.desc()).all()
        replies = user.comments_from.filter_by(topic_type='question_reply').order_by(Comment.timestamp.desc()).all()
        total = comments + replies
        return render_template('question/question_comments.html', form=form, comments=total,replies=replies, question=question)
    elif comment.topic_type=='answer':
        if form.validate_on_submit():
            comment = Comment.create(author=current_user._get_current_object(), user=user,
                              topic_type='answer_reply', body=form.body.data,answer=comment.answer)  # 被回复的是作者
            db.session.add(comment)
            db.session.commit()
            flash('回复成功', category='success')
            return redirect(url_for('.reply', id=comment.id))
        answer=comment.answer
        comments = user.comments.filter_by(topic_type='answer').order_by(Comment.timestamp.desc()).all()
        replies= user.comments_from.filter_by(topic_type='answer_reply').order_by(Comment.timestamp.desc()).all()
        total = comments + replies
        return render_template(answer/'answer_comments',form=form,comments=total,replies=replies,answer=answer)
    elif comment.topic_type=='reply':
        #楼中楼
        pass