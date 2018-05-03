from flask import request, render_template, redirect, url_for

from app import cache
from app.main.forms import SearchForm
from app.models import Post, current_app, Answer, Question, Tag, Topic
from app.constants import types
from app.main import main




def search():
    """抽离搜索业务逻辑,每个视图函数都支持"""
    form = SearchForm()
    if form.validate_on_submit():
        type = types[form.type.data]
        content = form.content.data
        return redirect(url_for('main.search_detail',type=type,q=content))



@main.route('/search',methods=['GET','POST'])
def search_detail():
    s=search()
    if s:
        return s
    type=request.args.get('type')
    q=request.args.get('q')
    page = request.args.get('page', 1, type=int)

    p_pagination=Post.query.whoosh_search(q, like=True).order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['ZHIDAO_POST_PER_PAGE'], error_out=False
        )
    q_pagination=Question.query.whoosh_search(q, like=True).order_by(Question.timestamp.desc()).paginate(
            page, per_page=current_app.config['ZHIDAO_QUESTION_PER_PAGE'], error_out=False
        )
    a_pagination=Answer.query.whoosh_search(q, like=True).order_by(Answer.timestamp.desc()).paginate(
            page, per_page=current_app.config['ZHIDAO_ANSWER_PER_PAGE'], error_out=False
        )
    t_pagination=Topic.query.whoosh_search(q,like=True).order_by(Topic.timestamp.desc()).paginate(
        page, per_page=current_app.config['ZHIDAO_TOPIC_PER_PAGE'], error_out=False
    )
    posts=p_pagination.items
    questions=q_pagination.items
    answers=a_pagination.items
    topics=t_pagination.items
    print(topics)
    context=dict(p_pagination=p_pagination,q_pagination=q_pagination,a_pagination=a_pagination,t_pagination=t_pagination,
                 posts=posts,questions=questions,answers=answers,topics=topics,
                 type=type,q=q)
    return render_template('search/search.html',**context)


