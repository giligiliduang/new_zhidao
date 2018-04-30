from flask import flash, redirect, url_for, render_template, abort, request, current_app
from flask_login import login_required,current_user

from app import db
from app.decorators import permission_required
from app.main import main
from app.main.forms import WriteAnswerForm, EditAnswerForm, CommentForm
from app.main.views.search import search
from app.models import Permission, Question, Answer, Comment
from app.signals import question_answer_add,answer_comment_add




@main.route('/question/<int:id>/write-answer',methods=['GET','POST'])
@login_required
@permission_required(Permission.CREATE_POSTS)
def write_answer(id):
    s = search()
    if s:
        return s
    question=Question.query.get_or_404(id)
    if question.answers.filter_by(author=current_user._get_current_object()).first():
        flash('你已经回答了该问题',category='warning')
        return redirect(url_for('.question',id=question.id))
    form=WriteAnswerForm()
    if form.validate_on_submit():
        Answer.create(body=form.body.data,question=question,
                      author=current_user._get_current_object(),anonymous=form.anonymous.data)
        question_answer_add.send(question)
        flash('添加回答成功',category='success')
        return redirect(url_for('.question',id=question.id))
    return render_template('answer/write_answer.html',form=form,question=question)

@main.route('/edit-answer/<int:id>',methods=['GET','POST'])
@login_required
@permission_required(Permission.CREATE_POSTS)
def edit_answer(id):
    s = search()
    if s:
        return s
    form=EditAnswerForm()
    answer=Answer.query.get_or_404(id)
    if current_user!=answer.author and not current_user.can(Permission.ADMINISTER):
        abort(403)#只有自己和管理员可以编辑文章,防止别人直接通过路由编辑文章
    if form.validate_on_submit():
        answer.body=form.body.data
        db.session.add(answer)
        flash('答案修改成功',category='success')
        return redirect(url_for('.question',id=answer.question_id))
    form.body.data=answer.body
    return render_template('answer/edit_answer.html',form=form,answer=answer)


@main.route('/answer/<int:id>/comments',methods=['GET','POST'])
@login_required
def answer_comments(id):
    s = search()
    if s:
        return s
    answer=Answer.query.get_or_404(id)
    form=CommentForm()
    if form.validate_on_submit():
        Comment.create(author=current_user._get_current_object(),answer=answer,
                        topic_type='answer',body=form.body.data)
        answer_comment_add.send(answer)
        flash('评论添加成功','success')
        return redirect(url_for('.answer_comments',id=answer.id))
    page=request.args.get('page',1,type=int)
    pagination=answer.comments.filter_by(topic_type='answer').order_by(Comment.timestamp.desc()).\
                paginate(page,per_page=current_app.config['ZHIDAO_COMMENT_PER_PAGE'],error_out=False)
    comments=pagination.items
    context=dict(form=form,pagination=pagination,comments=comments,answer=answer)
    return render_template('answer/answer_comments.html',**context)
