# -*- coding: utf-8 -*-
__author__ = 'giligilduang'

from app.models import Comment, Question, User, Reply
from flask import current_app, request
import unittest
from app import db, create_app


class CommentTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        self.app_context.pop()
        db.drop_all()

    def test_question_comment(self):
        """
        测试评论添加删除
        以及回复添加删除
        :return:
        """
        u = User.create(username='dw', password='23366')
        u1 = User.create(username='dwwff', password='23366')
        question = Question.create(author=u, description='dwdwdgg?')
        self.assertTrue(question.undelete_comments.count() == 0)
        self.assertTrue(question.comments.count() == 0)
        c = Comment.create(author=u1, question=question, topic_type='question', body='fdjhfjdj')
        c1 = Comment.create(author=u1, question=question, topic_type='question', body='lgkjgfdjhfjdj')
        self.assertTrue(question.comments.count() == 2)
        self.assertTrue(question.undelete_comments.count() == 2)
        r = Reply.create(comment=c, author=u, body='kllfdd')
        r1 = Reply.create(comment=c, author=u1, user=u, body='ldkkkfg')
        self.assertTrue(c.replies.count() == 2)

        u.delete_comment(c)  # 先删除评论
        self.assertTrue(c.replies.count() == 2)  # 不会影响回复
        self.assertTrue(question.comments.count() == 2)
        self.assertTrue(question.undelete_comments.count() == 1)

        u.delete_reply(r)  # 删除一条回复
        self.assertTrue(c.replies.count() == 1)
        u.delete_reply(r1)#删除最后一条回复
        self.assertNotIn(c,question.comments.all())#c不应该在所有评论里面


