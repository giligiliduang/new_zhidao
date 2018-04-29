from flask import request, current_app, render_template, make_response, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.decorators import permission_required
from app.main import main
from app.main.forms import WriteArticleForm, EditArticleForm
from app.main.views import search, Post, CommentForm, Comment, abort
from app.models import Tag, Permission


@main.route('/posts',methods=['GET','POST'])
@login_required
def posts():
    s = search()
    if s:
        return s
    page=request.args.get('page',1,type=int)
    if request.cookies.get('post_order_by')=='timestamp':
        pagination=Post.query.order_by(Post.timestamp.desc()).paginate(
            page,per_page=current_app.config['ZHIDAO_POST_PER_PAGE'],error_out=False
        )
    elif request.cookies.get('post_order_by')=='likecount':

        pagination = Post.query.order_by(Post.liked_count.desc()).paginate(
            page, per_page=current_app.config['ZHIDAO_POST_PER_PAGE'], error_out=False
        )
    else:
        pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['ZHIDAO_POST_PER_PAGE'], error_out=False
        )
    posts=pagination.items
    tags=Tag.query.all()
    context=dict(posts=posts,pagination=pagination,tags=tags)
    return render_template('post/posts.html',**context)

@main.route('/post_order_by_timestamp')
def post_order_by_timestamp():
    resp=make_response(redirect(url_for('main.posts')))
    resp.set_cookie('post_order_by','timestamp',max_age=60*60)
    return resp

@main.route('/post_order_by_likecount')
def post_order_by_likecount():
    resp = make_response(redirect(url_for('main.posts')))
    resp.set_cookie('post_order_by', 'likecount', max_age=60 * 60)
    return resp


@main.route('/tag/<int:id>/posts',methods=['GET','POST'])
@login_required
def tag_posts(id):
    s = search()
    if s:
        return s
    tag=Tag.query.get_or_404(id)
    page=request.args.get('page',1,type=int)
    pagination=tag.posts.paginate(page,per_page=current_app.config['ZHIDAO_POST_PER_PAGE']
                                  ,error_out=False)#分页返回PostTag对象
    posts=[item.post for item in pagination.items]#提取post对象
    tags=Tag.query.all()
    context=dict(posts=posts,tags=tags,pagination=pagination)
    return render_template('post/posts.html',**context)


@main.route('/post<int:id>',methods=['GET','POST'])
@login_required
def post(id):
    """文章详情页"""
    s = search()
    if s:
        return s
    post=Post.query.get_or_404(id)
    form=CommentForm()
    if post.author!=current_user:
        post.browsed()
    if form.validate_on_submit():
        comment=Comment.create(author=current_user._get_current_object(),post=post,
                        body=form.body.data,topic_type='post')
        db.session.add(comment)
        db.session.commit()
        flash('评论添加成功','success')
        return redirect(url_for('.post',id=post.id))
    page=request.args.get('page',1,type=int)
    pagination=post.comments.filter_by(topic_type='post').\
        order_by(Comment.timestamp.desc()).paginate(page,per_page=current_app.config['ZHIDAO_COMMENT_PER_PAGE'],error_out=False)
    comments=pagination.items
    if post.disable_comment:
        return render_template('post/post.html',post=post)
    context=dict(form=form,pagination=pagination,comments=comments,post=post)
    return render_template('post/post.html',**context)





@main.route('/create-post',methods=['GET','POST'])
@login_required
@permission_required(Permission.CREATE_POSTS)
def create_post():
    s = search()
    if s:
        return s
    form=WriteArticleForm()
    if form.validate_on_submit():
        post=Post.create(title=form.title.data,body=form.body.data,
                  author=current_user._get_current_object(),
                  disable_comment=form.disable_comment.data)
        for each in form.tags.data:
            tag=Tag.query.get_or_404(each)
            if tag.add_post(post):
                db.session.add(tag)
                flash('标签{}添加成功'.format(tag.title),category='success')
        flash('文章添加成功',category='success')
        return redirect(url_for('.posts'))
    return render_template('post/create_post.html',form=form)


@main.route('/edit-post/<int:id>',methods=['GET','POST'])
@login_required
def edit_post(id):
    s = search()
    if s:
        return s
    form=EditArticleForm()
    post=Post.query.get_or_404(id)
    if current_user!=post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    if form.validate_on_submit():
        post.body=form.body.data
        db.session.add(post)
        flash('文章修改成功')
        return redirect(url_for('.post',id=post.id))
    form.body.data=post.body
    return render_template('post/edit_post.html',form=form,post=post)
