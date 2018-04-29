from flask import request, render_template

from app import cache
from app.main.forms import SearchForm
from app.models import Post, current_app, Answer,Question
from app.constants import types

@cache.cached(timeout=1,key_prefix='search')
def search():
    """抽离搜索业务逻辑,每个视图函数都支持"""
    page = request.args.get('page', 1, type=int)
    form = SearchForm()
    if form.validate_on_submit():
        type = types[form.type.data]
        content = form.content.data
        if type == '文章':
            pagination = Post.query.whoosh_search(content, like=True).order_by(Post.timestamp.desc()).paginate(
                page, per_page=current_app.config['ZHIDAO_POST_PER_PAGE'], error_out=False
            )
            posts = pagination.items
            return render_template('post/posts.html', posts=posts, pagination=pagination)
        elif type == '答案':
            pagination = Answer.query.whoosh_search(content, like=True).order_by(Answer.timestamp.desc()).paginate(
                page, per_page=current_app.config['ZHIDAO_ANSWER_PER_PAGE'], error_out=False
            )
            answers = pagination.items
            return render_template('answer/answers.html', answers=answers, pagination=pagination)
        elif type == '问题':
            pagination = Question.query.whoosh_search(content, like=True).order_by(Question.timestamp.desc()).paginate(
                page, per_page=current_app.config['ZHIDAO_QUESTION_PER_PAGE'], error_out=False
            )
            questions = pagination.items
            return render_template('question/questions.html', questions=questions, pagination=pagination)
        else:
            return None