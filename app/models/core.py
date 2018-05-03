from whoosh.analysis import SimpleAnalyzer
from datetime import datetime
from flask_login import UserMixin,AnonymousUserMixin
from .mixins import BaseMixin,DateTimeMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,BadSignature,SignatureExpired
from flask import current_app, request
import hashlib
from app import db,bcrypt,login_manager
from ..constants import default_tags
from sqlalchemy.ext.hybrid import hybrid_property,hybrid_method
from sqlalchemy.ext.associationproxy import association_proxy
from app.constants import topics
import forgery_py



class PostTag(db.Model,BaseMixin,DateTimeMixin):
    """关系表"""
    __tablename_='posttags'
    tag_id=db.Column(db.Integer,db.ForeignKey('tags.id'),primary_key=True)
    post_id=db.Column(db.Integer,db.ForeignKey('posts.id'),primary_key=True)


class Tag(db.Model,BaseMixin):
    __tablename__='tags'
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(64))#标签名称
    posts = db.relationship('PostTag', backref='tag', foreign_keys=[PostTag.tag_id], lazy='dynamic')
    post_count=db.Column(db.Integer)
    @staticmethod
    def generate_tags():
        for i in default_tags:
            Tag.create(title=i)


    @staticmethod
    def add_new_tag(title):
        """添加新的标签"""
        tag=Tag.query.filter_by(title=title).first()
        if not tag:
            Tag.create(title=title)
            return True
        return False

    def add_post(self,post):
        if not self.has_post(post):
            t=PostTag.create(tag=self,post=post)

            return True if t else False
        return False
    def remove_post(self,post):
        f=self.posts.filter_by(post_id=post.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()
            return True
        return False

    def has_post(self,post):
        return self.posts.filter_by(post_id=post.id).first() is not None
    def __repr__(self):
        return '<Tag{}>'.format(self.title)

class LikeComment(db.Model,DateTimeMixin,BaseMixin):
    like_comment_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    comment_liked_id=db.Column(db.Integer,db.ForeignKey('comments.id'),primary_key=True)


class Comment(db.Model,BaseMixin,DateTimeMixin):
    __tablename__='comments'
    id=db.Column(db.Integer,primary_key=True)
    question_id=db.Column(db.Integer,db.ForeignKey('questions.id'))#针对问题的评论
    answer_id=db.Column(db.Integer,db.ForeignKey('answers.id'))#针对答案的评论
    post_id=db.Column(db.Integer,db.ForeignKey('posts.id'))#针对文章的评论
    favorite_id = db.Column(db.Integer, db.ForeignKey('favorites.id'))#收藏夹评论
    topic_type = db.Column(db.String(64), default='')#五种类型,文章评论,问题评论,答案评论,回复(评论里面的评论),收藏夹评论
    author_id=db.Column(db.Integer,db.ForeignKey('users.id'))#评论用户id
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'))#评论目标用户id
    body=db.Column(db.Text)
    disabled=db.Column(db.Boolean,default=False)#管理员审查言论
    liked_comments = db.relationship('LikeComment', backref=db.backref('comment_liked', lazy='joined'),
                                  lazy='dynamic', foreign_keys=[LikeComment.comment_liked_id],
                                  cascade='all,delete-orphan')
    liked_count=db.Column(db.Integer,default=0)#以点赞数排序

    def count_ping(self):
        """点赞，取消赞之后调用"""
        self.liked_count = self.liked_comments.count()
        db.session.add(self)
        db.session.commit()

    def is_liked_by(self,user):
        return self.liked_comments.filter_by(like_comment_id=user.id).first() is not None

    def __repr__(self):
        return '<Comment {}>'.format(self.id)


class PostFavorite(db.Model,BaseMixin,DateTimeMixin):
    __tablename__='postfavorites'
    post_id=db.Column(db.Integer,db.ForeignKey('posts.id'),primary_key=True)
    favorite_id=db.Column(db.Integer,db.ForeignKey('favorites.id'),primary_key=True)


class LikePost(db.Model,BaseMixin,DateTimeMixin):
    like_post_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    post_liked_id=db.Column(db.Integer,db.ForeignKey('posts.id'),primary_key=True)

class Post(db.Model,BaseMixin,DateTimeMixin):
    __tablename__='posts'
    __searchable__=['title']
    __analyzer__=SimpleAnalyzer()
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(64))
    body=db.Column(db.Text)
    author_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    favorites = db.relationship('PostFavorite',backref='post',lazy='dynamic',foreign_keys=[PostFavorite.post_id])
    tags = db.relationship('PostTag', backref='post', foreign_keys=[PostTag.post_id], lazy='dynamic')#标签
    disable_comment=db.Column(db.Boolean,default=False)#是否禁止评论
    comments=db.relationship('Comment',backref='post',lazy='dynamic')#属于文章的评论
    browse_count = db.Column(db.Integer, default=0)  # 文章被浏览了多少次
    liked_posts=db.relationship('LikePost',backref=db.backref('post_liked',lazy='joined'),
                                lazy='dynamic',foreign_keys=[LikePost.post_liked_id],
                                cascade='all,delete-orphan')
    liked_count = db.Column(db.Integer, default=0)  # 以点赞数排序
    tag_count=db.Column(db.Integer)#标签数量
    comments_count=db.Column(db.Integer)





    def disable(self):
        self.disable_comment=True
        db.session.add(self)

    def browsed(self):
        count=self.browse_count
        count+=1
        self.browse_count=count
        db.session.add(self)
    def add_tag(self,tag):
        if not self.has_tag(tag):
            PostTag.create(post=self,tag=tag)
            return True
        return False
    def remove_tag(self,tag):
        f=self.tags.filter_by(tag_id=tag.id).first()
        if f:
            db.session.delete(f)
            return True
        return False
    def has_tag(self,tag):
        return self.tags.filter_by(tag_id=tag.id).first() is not None


    def is_liked_by(self,user):
        return self.liked_posts.filter_by(like_post_id=user.id).first() is not None


class LikeAnswer(db.Model,BaseMixin,DateTimeMixin):
    like_answer_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)#赞同回答的人
    answer_liked_id=db.Column(db.Integer,db.ForeignKey('answers.id'),primary_key=True)#被喜欢的回答
class AnswerFavorite(db.Model,BaseMixin,DateTimeMixin):
    __tablename__='answerfavorites'
    answer_id=db.Column(db.Integer,db.ForeignKey('answers.id'),primary_key=True)
    favorite_id=db.Column(db.Integer,db.ForeignKey('favorites.id'),primary_key=True)

class Answer(db.Model,BaseMixin,DateTimeMixin):
    __tablename__='answers'
    __searchable__=['body']
    __analyzer__=SimpleAnalyzer()
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.Text)#回答详情
    author_id=db.Column(db.Integer,db.ForeignKey('users.id'))#作者
    question_id=db.Column(db.Integer,db.ForeignKey('questions.id'))#属于哪个问题
    favorites = db.relationship('AnswerFavorite',lazy='dynamic',backref='answer',foreign_keys=[AnswerFavorite.answer_id])
    anonymous=db.Column(db.Boolean,default=False)#作者是否匿名回答
    disable_comment = db.Column(db.Boolean, default=False)  # 是否禁止评论
    comments = db.relationship('Comment', backref='answer', lazy='dynamic')
    liked_answers=db.relationship('LikeAnswer',backref=db.backref('answer_liked',lazy='joined'),
                                  lazy='dynamic',foreign_keys=[LikeAnswer.answer_liked_id],
                                  cascade='all,delete-orphan')
    liked_count = db.Column(db.Integer, default=0)  # 以点赞数排序
    comments_count=db.Column(db.Integer)

    def  count_ping(self):
        """点赞，取消赞之后调用"""
        self.liked_count=self.liked_answers.count()
        db.session.add(self)
        db.session.commit()
    def is_liked_by(self,user):
        return self.liked_answers.filter_by(like_answer_id=user.id).first() is not None


    def disable(self):
        self.disable_comment=True
        db.session.add(self)

    def __repr__(self):
        return '<Answer {}>'.format(self.id)


class FollowQuestion(db.Model,BaseMixin,DateTimeMixin):
    __tablename__='followquestions'
    follower_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)#关注问题的人
    followed_id=db.Column(db.Integer,db.ForeignKey('questions.id'),primary_key=True)#被关注的问题

class QuestionTopic(db.Model,BaseMixin,DateTimeMixin):
    """关系表多对多,单层话题结构"""
    __tablename__='questiontopics'
    topic_id=db.Column(db.Integer,db.ForeignKey('topics.id'),primary_key=True)
    question_id=db.Column(db.Integer,db.ForeignKey('questions.id'),primary_key=True)

class QuestionFavorite(db.Model,BaseMixin,DateTimeMixin):
    __tablename__='questionfavorites'
    question_id=db.Column(db.Integer,db.ForeignKey('questions.id'),primary_key=True)
    favorite_id=db.Column(db.Integer,db.ForeignKey('favorites.id'),primary_key=True)


class Question(db.Model,BaseMixin,DateTimeMixin):
    __tablename__='questions'
    __searchable__=['title']
    __analyzer__=SimpleAnalyzer()
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(64))#问题名称
    description=db.Column(db.String(128))#问题描述
    author_id=db.Column(db.Integer,db.ForeignKey('users.id'))#提出问题的人
    topics=db.relationship('QuestionTopic',backref='question',lazy='dynamic',foreign_keys=[QuestionTopic.question_id])#属于的话题
    favorites=db.relationship('QuestionFavorite',backref='question',lazy='dynamic',foreign_keys=[QuestionFavorite.question_id])
    answers=db.relationship('Answer',backref='question',lazy='dynamic')#回答者
    browse_count=db.Column(db.Integer,default=0)#问题被浏览了多少次
    anonymous=db.Column(db.Boolean,default=False)#是否匿名提问
    disable_comment = db.Column(db.Boolean, default=False)  # 是否禁止评论
    comments = db.relationship('Comment', backref='question', lazy='dynamic')
    followers=db.relationship('FollowQuestion',backref=db.backref('followed',lazy='joined'),
                              lazy='dynamic',foreign_keys=[FollowQuestion.followed_id],
                              cascade='all,delete-orphan')
    answers_count=db.Column(db.Integer)
    comments_count=db.Column(db.Integer)
    followers_count=db.Column(db.Integer)

    def disable(self):
        self.disable_comment=True
        db.session.add(self)
    @hybrid_property
    def browsed(self):
        return self.browse_count
    @browsed.setter
    def browsed(self,val):
        self.browse_count=val
        db.session.add(self)
        db.session.commit()
    def is_followed_by(self,user):
        return self.followers.filter_by(follower_id=user.id).first() is not None




    def __repr__(self):
        return '<Question {}>'.format(self.title)

class FollowTopic(db.Model,BaseMixin,DateTimeMixin):
    __tablename__='followtopics'
    follower_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    followed_id=db.Column(db.Integer,db.ForeignKey('topics.id'),primary_key=True)

class Topic(db.Model,BaseMixin,DateTimeMixin):
    __tablename__='topics'
    __analyzer__=SimpleAnalyzer()
    __searchable__=['title']
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(64))#话题名称
    description=db.Column(db.Text)#话题描述
    cover_url=db.Column(db.String(128))#封面图片
    cover_url_sm=db.Column(db.String(128))#封面缩略图片
    author_id=db.Column(db.Integer,db.ForeignKey('users.id'))#创建人
    followers = db.relationship('FollowTopic', backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic', foreign_keys=[FollowTopic.followed_id],
                                cascade='all,delete-orphan')
    questions=db.relationship('QuestionTopic',backref='topic',lazy='dynamic',foreign_keys=[QuestionTopic.topic_id])#包括的问题
    follower_count=db.Column(db.Integer)
    questions_count=db.Column(db.Integer)
    def __repr__(self):
        return '<Topic {}>'.format(self.title)

    def add_question(self,question):
        if not self.is_in_topic(question):
            QuestionTopic.create(topic=self,question=question)
            return True
        return False
    def remove_question(self,question):
        f=self.questions.filter_by(question_id=question.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_in_topic(self,question):

        return self.questions.filter_by(question_id=question.id).first() is not None

    @classmethod
    def topic_exists(cls,title):
        return cls.query.filter_by(title=title).first() is not None

    @classmethod
    def generate_topics(cls):
        for each in topics:
            Topic.create(title=each,description='话题描述')

    def is_followed_by(self,user):
        return self.followers.filter_by(follower_id=user.id).first() is not None




class FollowFavorite(db.Model,BaseMixin,DateTimeMixin):
    __tablename__='followfavorites'
    follower_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)#关注问题的人
    followed_id=db.Column(db.Integer,db.ForeignKey('favorites.id'),primary_key=True)#被关注的收藏夹


class Favorite(db.Model,BaseMixin,DateTimeMixin):
    """收藏夹"""
    __tablename__='favorites'
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(64))#收藏夹的名称
    description = db.Column(db.String(150))  # 描述
    public=db.Column(db.Boolean,default=True)#是否公开
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'))#用户
    questions=db.relationship('QuestionFavorite',backref='favorite',lazy='dynamic',foreign_keys=[QuestionFavorite.favorite_id])
    answers=db.relationship('AnswerFavorite',backref='favorite',lazy='dynamic',foreign_keys=[AnswerFavorite.favorite_id])
    posts=db.relationship('PostFavorite',backref='favorite',lazy='dynamic',foreign_keys=[PostFavorite.favorite_id])
    comments=db.relationship('Comment',backref='favorite',lazy='dynamic')
    followers = db.relationship('FollowFavorite', backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic', foreign_keys=[FollowFavorite.followed_id],
                                cascade='all,delete-orphan')
    answers_count = db.Column(db.Integer)
    posts_count=db.Column(db.Integer)
    comments_count = db.Column(db.Integer)
    followers_count = db.Column(db.Integer)

    def collect(self,item):
        if isinstance(item,Answer):
            self.collect_answer(item)
        elif isinstance(item,Question):
            self.collect_question(item)
        elif isinstance(item,Post):
            self.collect_post(item)
    def uncollect(self,item):
        if isinstance(item,Answer):
            self.uncollect_answer(item)
        elif isinstance(item,Question):
            self.uncollect_question(item)
        elif isinstance(item,Post):
            self.uncollect_post(item)

    def collect_question(self,question):
        if not self.has_collect_question(question):
            QuestionFavorite.create(favorite=self,question=question)
    def uncollect_question(self,question):
        f=self.questions.filter_by(question_id=question.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()
    def has_collect_question(self,question):
        return self.questions.filter_by(question_id=question.id).first() is not None

    def collect_answer(self,answer):
        if not self.has_collect_answer(answer):
            AnswerFavorite.create(favorite=self,answer=answer)
    def uncollect_answer(self,answer):
        f=self.answers.filter_by(answer_id=answer.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()
    def has_collect_answer(self,answer):
        return self.answers.filter_by(answer_id=answer.id).first() is not None

    def collect_post(self,post):
        if not self.has_collect_post(post):
            PostFavorite.create(favorite=self,post=post)
    def uncollect_post(self,post):
        f=self.posts.filter_by(post_id=post.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()
    def has_collect_post(self,post):
        return self.posts.filter_by(post_id=post.id).first() is not None

    def is_followed_by(self,user):
        return self.followers.filter_by(follower_id=user.id).first() is not None


class Permission():
    FOLLOW = 0x01
    COMMENT = 0x02
    CREATE_POSTS = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.String(64), default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')#角色与用户是一对多的关系

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.CREATE_POSTS, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.CREATE_POSTS |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role {}>'.format(self.name)

class Follow(db.Model,BaseMixin,DateTimeMixin):
    __tablename__='follows'
    follower_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)#关注者
    followed_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)#被关注着
#
# class Message(db.Model,BaseMixin,DateTimeMixin):
#     __tablename__='messages'
#     id=db.Column(db.Integer,primary_key=True)
#     sender_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
#     receiver_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
#     message_content=db.Column(db.Text)
#     message_type=db.Column(db.String(64))#消息类型,系统消息，普通消息
#
#     status=db.Column(db.String(64))#消息状态，已读，未读，删除




class User(db.Model,UserMixin,BaseMixin):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64))
    email=db.Column(db.String(64))
    password_hash=db.Column(db.String(64))
    name=db.Column(db.String(64))
    location=db.Column(db.String(64))
    job=db.Column(db.String(64))
    about_me=db.Column(db.String(64))
    avatar_hash = db.Column(db.String(32))#默认头像
    avatar_url_sm=db.Column(db.String(64))#自定义头像缩略图
    avatar_url_nm=db.Column(db.String(64))#自定义头像正常图
    last_seen=db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)#最近登录
    member_since=db.Column(db.DateTime,default=datetime.utcnow)#注册日期
    visited_count=db.Column(db.Integer,default=0)#个人主页被浏览次数
    confirmed=db.Column(db.Boolean,default=False)#是否已经认证
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
    questions = db.relationship('Question', backref='author', lazy='dynamic')  # 提出的问题
    answers = db.relationship('Answer', backref='author', lazy='dynamic')  # 用户的回答
    topics=db.relationship('Topic',backref='author',lazy='dynamic')#创建的话题
    posts=db.relationship('Post',backref='author',lazy='dynamic')#我的文章
    comments = db.relationship('Comment', backref='author', lazy='dynamic',foreign_keys=[Comment.author_id])#我的评论
    comments_from=db.relationship('Comment',backref='user',lazy='dynamic',foreign_keys=[Comment.user_id])#回复我的
    # private_messages=db.relationship('Message',backref='sender',lazy='dynamic',foreign_keys=[Message.sender_id])#我发送的私信
    # private_messages_from=db.relationship('Message',backref='receiver',lazy='dynamic',foreign_keys=[Message.receiver_id])#我接收的私信


    favorites=db.relationship('Favorite',backref='user',lazy='dynamic')#收藏夹
    followers=db.relationship('Follow',backref=db.backref('followed',lazy='joined'),
                              foreign_keys=[Follow.followed_id],lazy='dynamic',
                              cascade='all,delete-orphan')#关注者
    followed = db.relationship('Follow', backref=db.backref('follower', lazy='joined'),
                                foreign_keys=[Follow.follower_id], lazy='dynamic',
                                cascade='all,delete-orphan')#被关注者
    followed_questions=db.relationship('FollowQuestion',backref=db.backref('follower',lazy='joined'),
                                       foreign_keys=[FollowQuestion.follower_id],lazy='dynamic',
                                       cascade='all,delete-orphan')#关注的问题
    followed_favorites = db.relationship('FollowFavorite', backref=db.backref('follower', lazy='joined'),
                                         foreign_keys=[FollowFavorite.follower_id], lazy='dynamic',
                                         cascade='all,delete-orphan')  # 关注的收藏夹
    followed_topics=db.relationship('FollowTopic', backref=db.backref('follower', lazy='joined'),
                                         foreign_keys=[FollowTopic.follower_id], lazy='dynamic',
                                         cascade='all,delete-orphan')  # 关注的收藏夹
    answer_likes = db.relationship('LikeAnswer', backref=db.backref('like_answer', lazy='joined'),
                                    lazy='dynamic', foreign_keys=[LikeAnswer.like_answer_id],
                                    cascade='all,delete-orphan')#赞过的答案
    post_likes=db.relationship('LikePost',backref=db.backref('like_post',lazy='joined'),
                               lazy='dynamic',foreign_keys=[LikePost.like_post_id],
                               cascade='all,delete-orphan')
    comment_likes=db.relationship('LikeComment',backref=db.backref('like_comment',lazy='joined'),
                               lazy='dynamic',foreign_keys=[LikeComment.like_comment_id],
                               cascade='all,delete-orphan')


    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email==current_app.config['ZHIDAO_ADMIN']:
                self.role=Role.query.filter_by(permission=0xff).first()
            if self.role is None:
                self.role=Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        # if not self.is_following_user(self):
        #     self.follow(self)




    def follow(self,item):
        if isinstance(item,User):
            self.follow_user(item)
        elif isinstance(item,Question):
            self.follow_question(item)
        elif isinstance(item,Favorite):
            self.follow_favorite(item)
        elif isinstance(item,Topic):
            self.follow_topic(item)
        else:
            raise TypeError('参数错误')
    def unfollow(self,item):
        if isinstance(item,User):
            self.unfollow_user(item)
        elif isinstance(item,Question):
            self.unfollow_question(item)
        elif isinstance(item,Favorite):
            self.unfollow_favorite(item)
        elif isinstance(item,Topic):
            self.unfollow_topic(item)
        else:
            raise TypeError('参数错误')

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following_user(user):
                user.follow(user)
                db.session.add(user)


    def follow_user(self,user):
        if not self.is_following_user(user):
            Follow.create(follower=self,followed=user)

    def unfollow_user(self,user):
        f=self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following_user(self,user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by_user(self,user):
        return self.followers.filter_by(follower_id=user.id).first() is not None
    def is_friend(self,user):
        return self.is_following_user(user) and self.is_followed_by_user(user)

    def follow_question(self,question):
        if not self.is_following_question(question):
            FollowQuestion.create(follower=self,followed=question)

    def unfollow_question(self,question):
        f=self.followed_questions.filter_by(followed_id=question.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()
    def is_following_question(self,question):
        return self.followed_questions.filter_by(followed_id=question.id).first() is not None


    def follow_favorite(self,favorite):
        if not self.is_following_favorite(favorite):
            FollowFavorite.create(follower=self,followed=favorite)


    def unfollow_favorite(self,favorite):
        f=self.followed_favorites.filter_by(followed_id=favorite.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following_favorite(self,favorite):
        return self.followed_favorites.filter_by(followed_id=favorite.id).first() is not None

    def follow_topic(self,topic):
        if not self.is_following_topic(topic):
            FollowTopic.create(follower=self,followed=topic)
    def unfollow_topic(self,topic):
        f=self.followed_topics.filter_by(followed_id=topic.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following_topic(self,topic):
        return self.followed_topics.filter_by(followed_id=topic.id).first() is not None


    @property
    def followed_user_questions(self):
        """除了自己的关注的人的提问"""
        return Question.query.join(Follow,db.and_(Follow.followed_id==Question.author_id,Follow.followed_id!=self.id)).\
            filter(Follow.follower_id==self.id)

    @property
    def followed_user_answers(self):
        """
        除了自己的关注的人的回答
        :return:
        """
        return Answer.query.join(Follow,db.and_(Follow.followed_id==Answer.author_id,Follow.followed_id!=self.id)).\
            filter(Follow.follower_id==self.id)

    @property
    def followed_user_posts(self):
        return Post.query.join(Follow,db.and_(Follow.followed_id==Post.author_id,Follow.followed_id!=self.id)).\
            filter(Follow.follower_id==self.id)

    @property
    def followed_user_favorites(self):
        return Favorite.query.join(Follow,db.and_(Follow.followed_id==Favorite.user_id,Follow.followed_id!=self.id)).\
            filter(Follow.follower_id==self.id)
    def who_is_following_current_user_in_my_followed(self,user):
        """
        除自己之外我关注的人里面谁也关注了他,返回两个数据
        :param user:
        :return:
        """

        return [i.followed for i in self.followed.order_by(Follow.timestamp.desc()).all()
                if i.followed.is_following_user(user) and user!=i.followed][:2]


    def like(self,item):
        if isinstance(item,Answer):
            self.like_answer(item)
        elif isinstance(item,Post):
            self.like_post(item)
        elif isinstance(item,Comment):
            self.like_comment(item)

    def unlike(self,item):
        if isinstance(item,Answer):
            self.unlike_answer(item)
        elif isinstance(item,Post):
            self.unlike_post(item)
        elif isinstance(item,Comment):
            self.unlike_comment(item)


    def like_answer(self,answer):
        if not self.is_like_answer(answer):
            f=LikeAnswer.create(like_answer=self,answer_liked=answer)

    def like_post(self,post):
        if not self.is_like_post(post):
            f=LikePost.create(like_post=self,post_liked=post)

    def like_comment(self,comment):
        if not self.is_like_comment(comment):
            f=LikeComment.create(like_comment=self,comment_liked=comment)


    def unlike_answer(self,answer):
        f=self.answer_likes.filter_by(answer_liked_id=answer.id).first()
        if f:
            db.session.delete(f)

    def unlike_post(self,post):
        f=self.post_likes.filter_by(post_liked_id=post.id).first()
        if f:
            db.session.delete(f)

    def unlike_comment(self,comment):
        f=self.comment_likes.filter_by(comment_liked_id=comment.id).first()
        if f:
            db.session.delete(f)

    def is_like_answer(self,answer):
        return self.answer_likes.filter_by(answer_liked_id=answer.id).first() is not None

    def is_like_post(self,post):
        return self.post_likes.filter_by(post_liked_id=post.id).first() is not None

    def is_like_comment(self,comment):
        return self.comment_likes.filter_by(comment_liked_id=comment.id).first() is not None


    def has_collect_question(self,question):

        return any(quest.question==question  for favorite in self.favorites for quest in favorite.questions.all())

    def has_collect_answer(self,answer):
        return any(ans.answer == answer for favorite in self.favorites for ans in favorite.answers.all())

    def has_collect_post(self,post):
        return any(pos.post == post for favorite in self.favorites for pos in favorite.posts.all())


    def has_collect(self,item):
        if isinstance(item,Answer):
            return self.has_collect_answer(item)
        elif isinstance(item,Question):
            return self.has_collect_question(item)
        elif isinstance(item,Post):
            return self.has_collect_post(item)
        else:
            raise TypeError('参数类型错误')
    def collect(self,item,favorite):
        if isinstance(item,Answer):
            fa=self.favorites.filter_by(id=favorite.id).first()
            if fa:
                fa.collect_answer(item)
        if isinstance(item,Question):
            fa=self.favorites.filter_by(id=favorite.id).first()
            if fa:
                fa.collect_question(item)
        if isinstance(item,Post):
            fa=self.favorites.filter_by(id=favorite.id).first()
            if fa:
                fa.collect_post(item)

    def uncollect(self,item,favorite):
        if isinstance(item, Answer):
            fa = self.favorites.filter_by(id=favorite.id).first()
            if fa:
                fa.uncollect_answer(item)
        if isinstance(item, Question):
            fa = self.favorites.filter_by(id=favorite.id).first()
            if fa:
                fa.uncollect_question(item)
        if isinstance(item, Post):
            fa = self.favorites.filter_by(id=favorite.id).first()
            if fa:
                fa.uncollect_post(item)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://secure.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)



    @hybrid_property
    def visited(self):
        return self.visited_count

    @visited.setter
    def visited(self,val):
        self.visited_count=val
        db.session.add(self)
        db.session.commit()



    def can(self,permissions):
        return self.role is not None and (self.role.permissions&permissions)==permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)


    @property
    def password(self):
            raise AttributeError('禁止访问')
    @password.setter
    def password(self,password):
        self.password_hash = bcrypt.generate_password_hash(password)

    def verify_password(self,password):
        return bcrypt.check_password_hash(self.password_hash,password)

    def generate_confirm_token(self,experition=3600):
        """生成token"""
        s=Serializer(current_app.config['SECRET_KEY'],expires_in=experition)
        return s.dumps({'confirm.txt':self.id})
    def generate_reset_token(self,experition=60*60):
        """生成token"""
        s=Serializer(current_app.config['SECRET_KEY'],expires_in=experition)
        return s.dumps({'reset':self.id})
    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def reset_password(self,token,password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except:
            return False
        if data and data.get('reset')==self.id:
            self.password=password
            db.session.add(self)
            return True
        else:
            return False

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def confirm(self,token):
        """令牌验证,反序列化，数据存在并且令牌没被篡改,返回True"""
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except:
            return False
        if data and data.get('confirm.txt')==self.id:
            self.confirmed=True
            db.session.add(self)
            return True
        else:
            return False

    @staticmethod
    def verify_api_auth_token(token):
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user=User.query.get(data.get('id'))
        return user



    def __repr__(self):
        return '<User{}>'.format(self.username)

class Alembic(db.Model):
    __tablename__ = 'alembic_version'
    version_num = db.Column(db.String(32), primary_key=True, nullable=False)

    @staticmethod
    def clear_A():
        for a in Alembic.query.all():
            db.session.delete(a)
        db.session.commit()





class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False

    def is_administrator(self):
        return False

    def has_collect(self,item):
        return False
    def is_following_question(self,question):
        return False






@login_manager.user_loader
def load_user(id):
    return User.query.get_or_404(int(id))

login_manager.anonymous_user=AnonymousUser