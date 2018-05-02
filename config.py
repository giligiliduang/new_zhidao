import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ZHIDAO_MAIL_SUBJECT_PREFIX = '[ZHIDAO]'
    ZHIDAO_MAIL_SENDER = 'ZHIDAO Admin <zhidao@163.com>'
    ZHIDAO_ADMIN = os.environ.get('ZHIDAO_ADMIN') or 'zhidao'
    ZHIDAO_QUESTION_PER_PAGE=10
    ZHIDAO_ANSWER_PER_PAGE=10
    ZHIDAO_POST_PER_PAGE=15
    ZHIDAO_COMMENT_PER_PAGE=20
    ZHIDAO_FOLLOW_PER_PAGE=20
    ZHIDAO_LIKE_PER_PAGE=20
    WHOOSH_BASE='path/to/whoosh/base'
    UPLOADED_PHOTOS_DEST=os.getcwd() + '/app/static/photos/'
    SQLALCHEMY_RECORD_QUERIES=True
    FLASK_DB_QUERY_TIMEOUT=0.5
    FLASK_SLOW_DB_QUERY_TIME=0.2
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    DEBUG = True
    CACHE_TYPE = 'simple'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql://root:Bye0Bye6@localhost/new_zhidao'
        # 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    CELERY_BROKER_URL='redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
class TestingConfig(Config):
    SERVER_NAME='localhost.dev'
    WTF_CSRF_ENABLED=False
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