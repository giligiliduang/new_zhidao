from flask import flash, redirect, url_for, abort, render_template, make_response, request,current_app
from flask_login import login_required, current_user
from app import db
from app.main import main
from app.main.views.search import search
from app.models import User, Favorite, Permission, Answer, Post, Question, Comment,PostFavorite,QuestionFavorite
from app.main.forms import EditFavoriteForm, FavoriteForm, CollectForm, CommentForm
from app.signals import favorite_question_delete,favorite_question_add,\
    favorite_answer_delete,favorite_answer_add,favorite_post_add,favorite_post_delete


@main.route('/user/<username>/create-favorite',methods=['GET','POST'])
@login_required
def create_favorite(username):
    s = search()
    if s:
        return s
    user=User.query.filter_by(username=username).first()
    if current_user!=user and not current_user.can(Permission.ADMINISTER):
        flash('没有权限')
        return redirect(url_for('.user',username=user.username))
    form=FavoriteForm()
    if form.validate_on_submit():
        Favorite.create(title=form.title.data,description=form.description.data,
                          public=form.public.data,user=current_user._get_current_object())

        flash('新建了{}收藏夹'.format(form.title.data),category='info')
        return redirect(url_for('.user',username=user.username))
    return render_template('favorite/create_favorite.html',form=form)#渲染表单



@main.route('/user/<username>/favorite/<int:id>')
@login_required
def favorite(username,id):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('.index'))
    favor=Favorite.query.get_or_404(id)
    page=request.args.get('page',1,type=int)
    if not favor.public:
        if current_user!=favor.user and not current_user.can(Permission.ADMINISTER):
            abort(403)
    if request.cookies.get('favorite_items')=='2':
        pagination=favor.questions.order_by(QuestionFavorite.timestamp.desc()).paginate(
            page,per_page=current_app.config['ZHIDAO_QUESTION_PER_PAGE'],error_out=False
        )
        questions=[i.question for i in  pagination.items]
        type='question'
        print('favo q')
        return render_template('favorite/favorites.html',user=user,type=type,questions=questions,favorite=favor,pagination=pagination)
    elif request.cookies.get('favorite_items')=='1':
        pagination=favor.posts.order_by(PostFavorite.timestamp.desc()).paginate(
            page,per_page=current_app.config['ZHIDAO_POST_PER_PAGE'],error_out=False
        )
        posts=[i.post for i in  pagination.items]
        type='post'
        return render_template('favorite/favorites.html',user=user,type=type,posts=posts,favorite=favor,pagination=pagination)
    questions=favor.questions.all()
    return render_template('favorite/favorites.html',user=user,questions=questions,favorite=favor)


@main.route('/favorite/<int:id>/posts')
def favorite_posts(id):
    favorite=Favorite.query.get(id)
    if not favorite:
        flash('收藏夹不存在')
        return redirect(url_for('.user',username=favorite.user.username))
    resp=make_response(redirect(url_for('.favorite',username=favorite.user.username,id=favorite.id)))
    resp.set_cookie('favorite_items','1',24*60*60)
    return resp

@main.route('/favorite/<int:id>/questions')
def favorite_questions(id):
    favorite = Favorite.query.get(id)
    if not favorite:
        flash('收藏夹不存在')
        return redirect(url_for('.user', username=favorite.user.username))
    resp = make_response(redirect(url_for('.favorite', username=favorite.user.username, id=favorite.id)))
    resp.set_cookie('favorite_items', '2', 24 * 60 * 60)
    return resp









@main.route('/user/<username>/favorite/<int:id>/edit',methods=['GET','POST'])
@login_required
def edit_favorite(username,id):
    """
    编辑收藏夹
    :param username:
    :param id:
    :return:
    """
    s = search()
    if s:
        return s
    user=User.query.filter_by(username=username).first()
    favorite=user.favorites.filter_by(id=id).first()
    if current_user!=user and not current_user.can(Permission.ADMINISTER):
        flash('没有权限')
        return redirect(url_for('.user', username=user.username))
    form=EditFavoriteForm()
    if form.validate_on_submit():
        favorite.title=form.title.data
        favorite.description=form.description.data
        db.session.add(favorite)
        return redirect(url_for('.favorite',username=user.username,id=favorite.id))
    form.title.data=favorite.title
    form.description.data=favorite.description
    context=dict(form=form,favorite=favorite)
    return render_template('favorite/edit_favorite.html',**context)




@main.route('/collect/question/<int:id>',methods=['GET','POST'])
@login_required
def collect_question(id):
    s = search()
    if s:
        return s
    question=Question.query.get_or_404(id)
    if question.author==current_user:
        flash('不能收藏自己提出的问题')
        return redirect(url_for('.index'))
    form=CollectForm()
    if form.validate_on_submit():
        favorite = current_user.favorites.filter_by(id=form.favorite.data).first()#当前用户的文件夹
        favorite.collect_question(question)#收藏问题
        favorite_question_add.send(favorite)
        flash('收藏了问题{}'.format(question.title),category='info')
        return redirect(url_for('.favorite',username=current_user.username,id=favorite.id))
    return render_template('favorite/collect.html',form=form)

@main.route('/collect/answer/<int:id>',methods=['GET','POST'])
@login_required
def collect_answer(id):
    s = search()
    if s:
        return s
    answer=Answer.query.get_or_404(id)
    if answer.author==current_user:
        flash('不能收藏自己的问题')
        return redirect(url_for('.index'))
    form = CollectForm()
    if form.validate_on_submit():
        favorite=current_user.favorites.filter_by(id=form.favorite.data).first()
        favorite.collect_answer(answer)
        favorite_answer_add.send(favorite)
        flash('收藏了{}的答案'.format(answer.author.username),category='info')
        return redirect(url_for('.favorite', username=current_user.username, id=favorite.id))
    return render_template('favorite/collect.html', form=form)

@main.route('/collect/post/<int:id>',methods=['GET','POST'])
@login_required
def collect_post(id):
    s = search()
    if s:
        return s
    post=Post.query.get_or_404(id)
    if post.author==current_user:
        flash('不能收藏自己的文章')
        return redirect(url_for('.index'))
    form=CollectForm()
    if form.validate_on_submit():
        favorite = current_user.favorites.filter_by(id=form.favorite.data).first()
        favorite.collect_post(post)
        favorite_post_add.send(favorite)
        flash('收藏了{}的文章{}'.format(post.author.username,post.title), category='info')
        return redirect(url_for('.favorite', username=current_user.username, id=favorite.id))
    return render_template('favorite/collect.html', form=form)



@main.route('/user/<username>/favorite/<int:id>/comments',methods=['GET','POST'])
@login_required
def favorite_comments(username,id):
    s = search()
    if s:
        return s
    user=User.query.filter_by(username=username).first()
    favorite=Favorite.query.get_or_404(id)
    form=CommentForm()
    if form.validate_on_submit():
        comment=Comment.create(author=current_user._get_current_object(),body=form.body.data,
                        favorite=favorite)
        db.session.add(comment)
        db.session.commit()
        flash('评论添加成功')
        return redirect(url_for('.favorite_comments',username=user.username,id=favorite.id))
    page=request.args.get('page',1,type=int)
    pagination=favorite.comments.order_by(Comment.timestamp.desc()).paginate(page,
                per_page=current_app.config['ZHIDAO_COMMENT_PER_PAGE'],error_out=False)
    comments=pagination.items
    context=dict(form=form,pagination=pagination,comments=comments,user=user,favorite=favorite)
    return render_template('favorite/favorite_comments.html',**context)
