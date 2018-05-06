from  flask import Flask
from config import config
from .ext import db, bootstrap, login_manager, moment, mail, cache, bcrypt, photos, admin
from flask_uploads import configure_uploads, patch_request_class
import flask_whooshalchemyplus


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    flask_whooshalchemyplus.init_app(app)
    configure_uploads(app, photos)
    patch_request_class(app)
    admin.init_app(app)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
