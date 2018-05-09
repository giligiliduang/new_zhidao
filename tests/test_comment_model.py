# -*- coding: utf-8 -*-
__author__ = 'giligilduang'

from app.models import Comment
from flask import current_app,request
import unittest
from app import db, create_app


class CommentTestCase(unittest.TestCase):
    def setUp(self):
        self.app=create_app('testing')
        self.app_context=self.app.app_context()
        db.session.commit()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        self.app_context.pop()
        db.drop_all()


