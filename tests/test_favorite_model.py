import unittest

from app import create_app, db
from app.models import Post, Favorite, PostFavorite, Question, Answer


class FavoriteModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    def test_collect_post(self):
        p=Post.create(title='haha')
        f=Favorite.create(title='数学')

        self.assertListEqual(f.posts.all(),[])
        self.assertTrue(f.posts.count()==0)
        self.assertTrue(p.favorites.count()==0)
        f.collect(p)
        self.assertListEqual([i.post for i in f.posts.all()],[p])
        self.assertTrue(f.posts.count() == 1)
        self.assertTrue(p.favorites.count() == 1)
        self.assertTrue(f.has_collect_post(p))
        f.uncollect(p)
        self.assertTrue(f.posts.count() == 0)
        self.assertTrue(p.favorites.count() == 0)
        self.assertFalse(f.has_collect_post(p))

    def test_collect_question(self):
        q=Question.create(title='wdffd')
        f=Favorite.create(title='数学')

        self.assertListEqual(f.questions.all(), [])
        self.assertTrue(f.questions.count() == 0)
        self.assertTrue(q.favorites.count() == 0)
        f.collect(q)
        self.assertListEqual([i.question for i in f.questions.all()], [q])
        self.assertTrue(f.questions.count() == 1)
        self.assertTrue(q.favorites.count() == 1)
        self.assertTrue(f.has_collect_question(q))
        f.uncollect(q)
        self.assertTrue(f.questions.count() == 0)
        self.assertTrue(q.favorites.count() == 0)
        self.assertFalse(f.has_collect_question(q))

    def test_collect_answer(self):
        q=Question.create(title='dwwf')
        a=Answer.create(body='dwwdf',question=q)
        f = Favorite.create(title='数学')

        self.assertListEqual(f.answers.all(), [])
        self.assertTrue(f.answers.count() == 0)
        self.assertTrue(a.favorites.count() == 0)
        f.collect(a)
        self.assertListEqual([i.answer for i in f.answers.all()],[a])
        self.assertTrue(f.answers.count() == 1)
        self.assertTrue(a.favorites.count() == 1)
        self.assertTrue(f.has_collect_answer(a))
        f.uncollect(a)
        self.assertTrue(f.answers.count() == 0)
        self.assertTrue(a.favorites.count() == 0)
        self.assertFalse(f.has_collect_answer(a))



