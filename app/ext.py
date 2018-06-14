from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_moment import Moment
from flask_cache import Cache
from flask_uploads import UploadSet, IMAGES
from flask_admin import Admin



db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.login_message = '请登录'
login_manager.login_message_category = 'info'
login_manager.login_view = 'auth.login'
login_manager.refresh_view='auth.login'
moment = Moment()
mail = Mail()
cache = Cache()
bcrypt = Bcrypt()
photos = UploadSet('photos', IMAGES)
admin = Admin(name='吱道后台管理', template_mode='bootstrap3')
