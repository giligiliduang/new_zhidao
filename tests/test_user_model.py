
import time

import datetime

from app import create_app, db

import unittest
from app.models import User, Role, Permission, AnonymousUser, Follow, Question, FollowQuestion, FollowFavorite, \
    Favorite, Topic, FollowTopic


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password = 'dog')
        self.assertTrue(u.password_hash is not None)

    def test_password_getter(self):
        u = User(password='dog')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password = 'dog')
        self.assertFalse(u.verify_password('cat'))
        self.assertTrue(u.verify_password('dog'))

    def test_valid_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirm_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(password='cat')
        u2 = User(password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirm_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirm_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    def test_password_salts_are_random(self):
        u = User(password = 'dog')
        u2 = User(password = 'dog')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_roles_and_permissions(self):
        Role.insert_roles()
        u = User(email='lihui@fanxiangce.com', password="secret")
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.CREATE_POSTS))



    def test_gravatar(self):
        u = User(email='john@example.com', password='cat')
        with self.app.test_request_context('/'):
            gravatar = u.gravatar()
            gravatar_256 = u.gravatar(size=256)
            gravatar_pg = u.gravatar(rating='pg')
            gravatar_retro = u.gravatar(default='retro')
        with self.app.test_request_context('/', base_url='https://example.com'):
            gravatar_ssl = u.gravatar()
        self.assertTrue('http://www.gravatar.com/avatar/' +
                        'd4c74594d841139328695756648b6bd6' in gravatar)
        self.assertTrue('s=256' in gravatar_256)
        self.assertTrue('r=pg' in gravatar_pg)
        self.assertTrue('d=retro' in gravatar_retro)
        self.assertTrue('https://secure.gravatar.com/avatar/' +
                        'd4c74594d841139328695756648b6bd6' in gravatar_ssl)


    def test_self_follows(self):
        u1 = User.create(email='john@example.com', password='cat')
        self.assertTrue(u1.is_following_user(u1))
        self.assertTrue(u1.is_followed_by_user(u1))



    def test_user_follows(self):
        u1 = User.create(email='john@example.com', password='cat')
        u2 = User.create(email='susan@example.org', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertFalse(u1.is_following_user(u2))
        self.assertFalse(u1.is_followed_by_user(u2))
        timestamp_before = datetime.datetime.utcnow()
        u1.follow(u2)
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.datetime.utcnow()
        self.assertTrue(u1.is_following_user(u2))
        self.assertFalse(u1.is_followed_by_user(u2))
        self.assertTrue(u2.is_followed_by_user(u1))
        self.assertTrue(u1.followed.count() == 2)
        self.assertTrue(u2.followers.count() == 2)
        f = u1.followed.all()[-1]
        self.assertTrue(f.followed == u2)
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        f = u2.followers.all()[-1]
        self.assertTrue(f.follower == u1)
        u1.unfollow(u2)
        db.session.add(u1)
        db.session.commit()
        self.assertTrue(u1.followed.count() == 1)
        self.assertTrue(u2.followers.count() == 1)
        self.assertTrue(Follow.query.count() == 2)
        u2.follow(u1)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        db.session.delete(u2)
        db.session.commit()
        self.assertTrue(Follow.query.count() == 1)

    def test_question_follows(self):
        u1 = User.create(email='john@example.com', password='cat')
        u2=User.create(email='lao@163.com',password='mouse')
        q1=Question.create(title='你见过的最漂亮的人',author=u2)
        db.session.add_all([u1,u2,q1])
        db.session.commit()
        self.assertFalse(u1.is_following_question(q1))
        self.assertFalse(q1.is_followed_by(u1))
        timestamp_before = datetime.datetime.utcnow()
        u1.follow(q1)
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.datetime.utcnow()
        self.assertTrue(u1.is_following_question(q1))
        self.assertTrue(q1.is_followed_by(u1))
        self.assertTrue(q1.followers.count()==1)
        self.assertTrue(u1.followed_questions.count()==1)
        f=u1.followed_questions.all()[0]
        self.assertTrue(f.followed==q1)
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        s=q1.followers.all()[0]
        self.assertTrue(s.follower==u1)
        u1.unfollow(q1)
        db.session.add(u1)
        db.session.commit()
        self.assertFalse(u1.is_following_question(q1))
        self.assertFalse(q1.is_followed_by(u1))
        self.assertTrue(u1.followed_questions.count()==0)
        self.assertTrue(q1.followers.count()==0)
        self.assertTrue(FollowQuestion.query.count()==0)

    def test_favorite_follows(self):
        u1=User.create(email='wanghua@qq.com',password='meijd')
        u2=User.create(email='lihua@qq.com',password='laodi')
        favor=Favorite.create(title='美术',user=u2)
        db.session.add_all([u1,u2,favor])
        db.session.commit()
        self.assertFalse(u1.is_following_favorite(favor))
        self.assertFalse(favor.is_followed_by(u1))
        timestamp_before = datetime.datetime.utcnow()
        u1.follow(favor)
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.datetime.utcnow()
        self.assertTrue(u1.is_following_favorite(favor))
        self.assertTrue(favor.is_followed_by(u1))
        self.assertTrue(u1.followed_favorites.count()==1)
        self.assertTrue(favor.followers.count()==1)
        f = u1.followed_favorites.all()[0]
        self.assertTrue(f.followed == favor)
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        u1.unfollow(favor)
        db.session.add(u1)
        db.session.commit()
        self.assertFalse(u1.is_following_favorite(favor))
        self.assertFalse(favor.is_followed_by(u1))
        self.assertTrue(u1.followed_favorites.count()==0)
        self.assertTrue(favor.followers.count()==0)
        self.assertTrue(FollowFavorite.query.count()==0)


    def test_topic_follows(self):
        u1 = User.create(email='wanghua@qq.com', password='meijd')
        u2 = User.create(email='lihua@qq.com', password='laodi')
        topic = Topic.create(title='美术', author=u2)
        db.session.add_all([u1, u2, topic])
        db.session.commit()
        self.assertFalse(u1.is_following_topic(topic))
        self.assertFalse(topic.is_followed_by(u1))
        timestamp_before = datetime.datetime.utcnow()
        u1.follow(topic)
        timestamp_after = datetime.datetime.utcnow()
        self.assertTrue(u1.is_following_topic(topic))
        self.assertTrue(topic.is_followed_by(u1))
        self.assertTrue(u1.followed_topics.count()==1)
        self.assertTrue(topic.followers.count()==1)
        t=u1.followed_topics.all()[0]
        self.assertTrue(t.followed==topic)
        self.assertTrue(timestamp_before <= t.timestamp <= timestamp_after)

        u1.unfollow(topic)
        db.session.add(u1)
        db.session.commit()
        self.assertFalse(u1.is_following_topic(topic))
        self.assertFalse(topic.is_followed_by(u1))
        self.assertTrue(u1.followed_topics.count() == 0)
        self.assertTrue(topic.followers.count() == 0)
        self.assertTrue(FollowTopic.query.count() == 0)


