
from flask import render_template,redirect,url_for,abort,request,session,current_app

from app import photos, db
from app.main import main
from app.models import Topic, User, QuestionTopic, FollowTopic
from flask_login import login_required,current_user
from app.main.views.search import search
from app.decorators import admin_required
from ..forms.topic import CreateTopicForm
from app.utils import image_resize

@main.route('/topics',methods=['GET','POST'])
def topics():
    s=search()
    if s:
        return s
    items=Topic.query
    l_items=[item for (index,item) in enumerate(items.all(),0) if index%2==0]
    r_items=[item for (index,item) in enumerate(items.all(),0) if index%2!=0]
    hot_topics=items.order_by(Topic.follower_count.desc()).limit(3)#关注最多的三个话题
    context=dict(l_items=l_items,r_items=r_items,topics=topics,hot_topics=hot_topics)
    return render_template('topic/topics.html',**context)

#查询热门回答者,查询出该话题的所有问题,从用户的回答过滤出属于该这些问题的回答
@main.route('/topic/<int:id>',methods=['GET','POST'])
def topic_detail(id):
    s = search()
    if s:
        return s
    topic=Topic.query.get_or_404(id)
    questions=[i.question for i in topic.questions.all()]
    context=dict(questions=questions,topic=topic)

    return render_template('topic/topic.html',**context)

@main.route('/topic/<id>/followers',methods=['GET','POST'])
def topic_followers(id):
    s = search()
    if s:
        return s
    topic=Topic.query.get_or_404(id)
    page=request.args.get('page',1,type=int)

    pagination=topic.followers.order_by(FollowTopic.timestamp.desc()).paginate(page,per_page=current_app.config['ZHIDAO_FOLLOW_PER_PAGE'],
                                        error_out=False)
    follows=[i.follower for i in pagination.items]
    session['topic_id']=topic.id
    context=dict(pagination=pagination,follows=follows,topic=topic)
    return render_template('topic/topic_followers.html',**context)

@main.route('/create_topic',methods=['GET','POST'])
@login_required
@admin_required
def create_topic():
    form=CreateTopicForm()
    if form.validate_on_submit():
        topic=Topic.create(title=form.title.data,description=form.description.data)
        filename=photos.save(form.photo.data)
        photo_url=photos.url(form.photo.data)
        cover_url_sm=image_resize(filename,30)
        cover_url=image_resize(filename,400)
        topic.cover_url=cover_url
        topic.cover_url_sm=cover_url_sm
        db.session.add(topic)
        db.session.commit()
        return redirect(url_for('.topics'))
    return render_template('topic/create_topic.html',form=form)