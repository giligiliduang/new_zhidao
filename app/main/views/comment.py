from flask import flash, redirect, url_for, abort
from flask_login import current_user

from app import db
from app.main import main
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
