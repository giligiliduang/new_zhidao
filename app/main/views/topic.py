
from flask import render_template,redirect,url_for,abort,request,session,current_app
from app.main import main
from app.models import Topic, User, QuestionTopic, FollowTopic


@main.route('/topics')
def topics():
    items=Topic.query
    l_items=[item for (index,item) in enumerate(items.all(),0) if index%2==0]
    r_items=[item for (index,item) in enumerate(items.all(),0) if index%2!=0]
    hot_topics=items.order_by(Topic.follower_count.desc()).limit(3)#关注最多的三个话题
    context=dict(l_items=l_items,r_items=r_items,topics=topics,hot_topics=hot_topics)
    return render_template('topic/topics.html',**context)

#查询热门回答者,查询出该话题的所有问题,从用户的回答过滤出属于该这些问题的回答
@main.route('/topic/<int:id>')
def topic_detail(id):
    topic=Topic.query.get_or_404(id)
    questions=[i.question for i in topic.questions.all()]
    context=dict(questions=questions,topic=topic)

    return render_template('topic/topic.html',**context)

@main.route('/topic/<id>/followers')
def topic_followers(id):
    topic=Topic.query.get_or_404(id)
    page=request.args.get('page',1,type=int)

    pagination=topic.followers.order_by(FollowTopic.timestamp.desc()).paginate(page,per_page=current_app.config['ZHIDAO_FOLLOW_PER_PAGE'],
                                        error_out=False)
    follows=[i.follower for i in pagination.items]
    session['topic_id']=topic.id
    context=dict(pagination=pagination,follows=follows,topic=topic)
    return render_template('topic/topic_followers.html',**context)
