import os

basedir = os.path.abspath(os.path.dirname(__file__))
mysql_username = 'root'
mysql_pwd = 'Bye0Bye6'


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ZHIDAO_MAIL_SUBJECT_PREFIX = '[ZHIDAO]'
    ZHIDAO_MAIL_SENDER = 'ZHIDAO Admin <zhidao@163.com>'
    ZHIDAO_ADMIN = os.environ.get('ZHIDAO_ADMIN') or 'zhidao'
    ZHIDAO_USER_PER_PAGE = 10
    ZHIDAO_QUESTION_PER_PAGE = 10
    ZHIDAO_ANSWER_PER_PAGE = 10
    ZHIDAO_FAVORITE_PER_PAGE = 10
    ZHIDAO_POST_PER_PAGE = 15
    ZHIDAO_TOPIC_PER_PAGE = 10
    ZHIDAO_MESSAGE_PER_PAGE = 10
    ZHIDAO_COMMENT_PER_PAGE = 20
    ZHIDAO_FOLLOW_PER_PAGE = 20
    ZHIDAO_LIKE_PER_PAGE = 20
    WHOOSH_BASE = 'path/to/whoosh/base'
    UPLOADED_PHOTOS_DEST = os.path.join(os.path.join(basedir, 'static'), 'photos')
    SQLALCHEMY_RECORD_QUERIES = True
    FLASK_DB_QUERY_TIMEOUT = 0.5
    FLASK_SLOW_DB_QUERY_TIME = 0.2

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """
    开发环境使用mysql，用户名和密码需要修改mysql_username和mysql_pwd
    """
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    DEBUG = True
    CACHE_TYPE = 'simple'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'mysql://{}:{}@localhost/new_zhidao'.format(mysql_username, mysql_pwd)




class TestingConfig(Config):
    SERVER_NAME = 'localhost.dev'
    WTF_CSRF_ENABLED = False
    CACHE_TYPE = 'simple'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
