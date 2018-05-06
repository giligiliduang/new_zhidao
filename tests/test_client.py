from app import create_app, db
import unittest
from app.models import User, Role, Topic
from flask import url_for


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        Topic.generate_topics()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @unittest.skip('dww')
    def test_home_page(self):
        rv = self.client.get(url_for('main.index'))
        self.assertTrue('写文章' in rv.get_data(as_text=True))

    @unittest.skip('dwwd')
    def test_register_and_login(self):
        data = {
            'email': 'john@163.com',
            'username': 'laodi',
            'password': 'Bye0Bye6',
            'password2': 'Bye0Bye6'

        }
        response = self.client.post(url_for('auth.register'), data=data)
        self.assertTrue(response.status_code == 302)

        response = self.client.post(url_for('auth.login', data={
            'email': 'john@163.com',
            'password': 'Bye0Bye6'
        }), follow_redirects=True)  # 登录界面
        data = response.get_data(as_text=True)
        self.assertTrue('注册成功' in data)
        user = User.query.filter_by(email='john@163.com').first()
        token = user.generate_confirm_token()
        self.client.get(url_for('auth.confirm', token=token), follow_redirects=True)

        response = self.client.post(url_for('auth.login', data={
            'email': 'john@163.com',
            'password': 'Bye0Bye6'
        }), follow_redirects=True)  # 登录界面
        print(response.get_data(as_text=True))
        self.assertTrue('登录成功' in response.get_data(as_text=True))

        response = self.client.get('auth.logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue('退出登录' in data)

    def test_add_post(self):
        u = User.create(username='lala', password='dwff', email='1512fdfd@qq.com', confirmed=True)

        res = self.client.post(url_for('auth.login'), data={
            'email': '1512fdfd@qq.com',
            'password': 'dwff'
        }, follow_redirects=False)
        print(res.get_data(as_text=True))
        self.assertTrue(res.status_code == 302)
        data = {
            'title': '那天说话'
        }
        response = self.client.post(url_for('main.create_post'), data=data)
        self.assertTrue('那天说话' in response.get_data(as_text=True))
