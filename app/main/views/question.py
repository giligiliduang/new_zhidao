from app import db
from app.decorators import permission_required
from app.main import main
from flask import request, current_app, make_response, render_template, redirect, flash, url_for, abort, g, session
from flask_login import current_user, login_required

from app.main.forms import CommentForm, EditQuestionForm, Topic, QuestionForm
from app.signals import question_unfollow, question_follow, question_answer_add, question_browsed, question_comment_add

from app.main.views.search import search
from app.models import Question, Answer, Comment, Permission, FollowQuestion, User
from collections import deque


@main.route('/question/<int:id>', methods=['GET', 'POST'])
def question(id):
    """
    问题详情页
    :param id:
    :return:
    """

    s = search()
    if s:
        return s
    page = request.args.get('page', 1, type=int)
    question = Question.query.get_or_404(id)
    pagination = question.answers.order_by(Answer.timestamp.desc()). \
        paginate(page, per_page=current_app.config['ZHIDAO_ANSWER_PER_PAGE'], error_out=False)
    answers = pagination.items
    topics = [i.topic for i in question.topics.all()]
    if current_user != question.author:
        question_browsed.send(question)  # 发送信号更新
    recent_q = request.cookies.get('recent_q', '')
    ques_id = str(question.id)
    if recent_q == '':
        # 第一次点击
        recent_q = deque(maxlen=5)
        if ques_id in recent_q:
            recent_q.remove(ques_id)  # 先删除
            recent_q.appendleft(ques_id)  # 再在前面添加
        else:
            recent_q.appendleft(ques_id)
        recent_q = ','.join(recent_q)  # 拼接字符串 类似'4,8,6,9'
        a_context = dict(question=question, answers=answers, pagination=pagination, topics=topics)
        resp = make_response(render_template('question/question.html', **a_context))
        resp.set_cookie('recent_q', recent_q)
        return resp
    else:
        arr = recent_q.split(',')
        recent_q = deque(arr, maxlen=5)  # 生成deque
        if ques_id in recent_q:
            recent_q.remove(ques_id)  # 先删除
            recent_q.appendleft(ques_id)  # 再在前面添加
        else:
            recent_q.appendleft(ques_id)
        recent_q_count=len(recent_q)
        session['recent_q_count']=recent_q_count
        recent_q = ','.join(recent_q)  # 拼接字符串 类似'4,8,6,9'
        context = dict(question=question, answers=answers, pagination=pagination, topics=topics)
        resp = make_response(
            render_template('question/question.html', **context))
        resp.set_cookie('recent_q', recent_q)
        return resp


@main.route('/recent_questions')
def recent_questions():
    ids = request.cookies.get('recent_q', '')
    if ids == '':
        questions = None
    else:
        ids = [int(i) for i in ids.split(',')]  # 只有一个元素也可以
        questions = [Question.query.get_or_404(id) for id in ids]
    context = dict(questions=questions)
    return render_template('question/recent_questions.html', **context)


@main.route('/question/<int:id>/comments', methods=['GET', 'POST'])
@login_required
def question_comments(id):
    s = search()
    if s:
        return s
    form = CommentForm()
    question = Question.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    if form.validate_on_submit():
        Comment.create(author=current_user._get_current_object(), question=question,
                       body=form.body.data, topic_type='question')
        question_comment_add.send(question)
        flash('评论添加成功', category='success')
        return redirect(url_for('.question_comments', id=question.id))

    pagination = question.comments.filter_by(topic_type='question').order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['ZHIDAO_COMMENT_PER_PAGE'], error_out=False
    )
    comments = pagination.items
    context = dict(pagination=pagination, comments=comments, question=question, form=form)
    return render_template('question/question_comments.html', **context)


@main.route('/edit-question/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.CREATE_POSTS)
def edit_question(id):
    s = search()
    if s:
        return s
    form = EditQuestionForm()
    question = Question.query.get_or_404(id)
    if current_user != question.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    if form.validate_on_submit():
        question.description = form.description.data  # 修改问题描述
        question.anonymous = form.anonymous.data  # 选择取消匿名
        db.session.add(question)
        return redirect(url_for('.question', id=question.id))
    form.description.data = question.description
    form.anonymous.data = question.anonymous
    context = dict(form=form, question=question)
    return render_template('question/edit_question.html', **context)


@main.route('/render-question', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.CREATE_POSTS)
def pose_question():
    """
    提出问题
    :return:
    """
    s = search()
    if s:
        return s
    form = QuestionForm()
    if form.validate_on_submit():

        question = Question.create(author=current_user._get_current_object(), title=form.title.data,
                                   description=form.description.data, anonymous=form.anonymous.data)

        for each in form.topic.data:
            topic = Topic.query.get(each)
            if topic.add_question(question):
                flash('添加到话题:{}'.format(topic.title), 'success')

        flash('提问成功')
        return redirect(url_for('.index'))
    return render_template('question/pose_question.html', form=form)


@main.route('/question/<int:id>/followers', methods=['GET', 'POST'])
def question_followers(id):
    s = search()
    if s:
        return s
    question = Question.query.get_or_404(id)
    if question is None:
        flash('问题不存在')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = question.followers.order_by(FollowQuestion.timestamp.desc()). \
        paginate(page, per_page=current_app.config['ZHIDAO_FOLLOW_PER_PAGE'], error_out=False)
    follows = [item.follower for item in pagination.items]  # 关注问题的人
    title = '关注问题{}的人'.format(question.title)
    style = 'question_followers'
    context = dict(pagination=pagination, follows=follows,
                   question=question, title=title, style=style, user=question.author)
    return render_template('user/user_follows.html', **context)


@main.route('/question<id>/invite', methods=['GET', 'POST'])
@login_required
def invite(id):
    """
    邀请关注该话题的人来回答问题
    :param id:
    :return:
    """
    question = Question.query.get_or_404(id)
    topics = [i.topic for i in question.topics.all()]
    author = question.author
    users = [i for i in User.query.all() for j in topics if i.is_following_topic(j) and i != current_user]

    if current_user == author:
        name = current_user.username
        url = url_for('main.question', id=question.id, _external=True)
        [current_user.send_invitation('{name}邀请你回答问题:{url}'.format(name=name, url=url), i) for i in users]
        flash('成功发出邀请')
        return redirect(url_for('main.question',id=question.id))
    flash('你不是作者')
    return redirect(url_for('main.question', id=question.id))