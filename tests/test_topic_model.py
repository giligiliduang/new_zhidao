import unittest
from app import db,create_app
from app.models import Topic,Question,QuestionTopic

class TopicModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_remove_question(self):
        topic=Topic.create(title='摄影')
        question=Question.create(title='好吗?')
        questions=[i.question for i in topic.questions.all()]
        self.assertListEqual(questions,[])
        self.assertTrue(topic.questions.count()==0)
        topic.add_question(question)
        questions = [i.question for i in topic.questions.all()]
        self.assertListEqual(questions,[question])
        self.assertTrue(topic.questions.count()==1)
        topic.remove_question(question)
        self.assertFalse(topic.is_in_topic(question))
        self.assertTrue(topic.questions.count()==0)
