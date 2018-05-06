import unittest
from app import create_app, db
from app.models import Tag, Post



class TestPostModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Tag.generate_tags()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_remove_tag(self):
        """
        测试添加删除标签
        :return:
        """
        post = Post.create(title='hahd')
        tags = [i.tag for i in post.tags.all()]
        self.assertListEqual(tags, [])
        self.assertTrue(post.tags.count() == 0)
        tag = Tag.create(title='摄影')
        post.add_tag(tag)
        tags = [i.tag for i in post.tags.all()]
        self.assertListEqual(tags, [tag])
        self.assertTrue(post.tags.all() == tag.posts.all())
        post.remove_tag(tag)
        self.assertTrue(post.tags.count() == 0)
