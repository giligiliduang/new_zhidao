from flask import request, current_app, render_template

from app.main import main
from app.main.views.search import search
from app.models import Question


@main.route('/',methods=['GET','POST'])
def index():
    page = request.args.get('page', 1, type=int)
    s=search()
    if s:
        return s
    pagination=Question.query.order_by(Question.timestamp.desc()).paginate(
        page,per_page=current_app.config['ZHIDAO_QUESTION_PER_PAGE'],error_out=False
    )
    questions=pagination.items
    context=dict(questions=questions,pagination=pagination)
    return render_template('index/index.html',**context)
