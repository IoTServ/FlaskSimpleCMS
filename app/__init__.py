from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_wtf.csrf import CsrfProtect
from flask_moment import Moment
from flask_cache import Cache
from config import Config
from flask_mail import Mail
from flask_compress import Compress

db = SQLAlchemy()
bootstrap = Bootstrap()
moment = Moment()
csrf = CsrfProtect()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
cache = Cache()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)
    #CsrfProtect(app)

    db.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    Compress(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/user')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .username import username as username_blueprint
    app.register_blueprint(username_blueprint, url_prefix='/zhuye')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    from .mip import mip as mip_blueprint
    app.register_blueprint(mip_blueprint, url_prefix='/mip')

    return app
