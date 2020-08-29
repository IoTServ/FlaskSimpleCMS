#coding: utf-8
import hashlib,urllib2,json
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from . import cache
from flask import current_app

class Permission:
    COMMON = 0x01
    ADMINISTER = 0x80

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.COMMON, True),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    initial_email = db.Column(db.String(64))
    qq = db.Column(db.BigInteger)
    tel=db.Column(db.BigInteger)
    wechat=db.Column(db.String(32))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    com_name=db.Column(db.String(64))
    username = db.Column(db.String(32), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    avatar_hash = db.Column(db.String(32))
    articles = db.relationship('Article', backref='author', lazy='dynamic')
    sign_date = db.Column(db.Date,default=datetime.utcnow)
    gravatar_url = db.Column(db.String(256))
    coin = db.Column(db.Integer,default=0)
    confirmed = db.Column(db.Boolean, default=False)

    banded = db.Column(db.Boolean,default=False)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def generate_repassword_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'repassword': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        return True
    @staticmethod
    def repassword(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            id = data.get('repassword')
            print id
        except:
            return False
        if User.query.filter_by(id=id).first():
            user=User.query.filter_by(id=id).first()
            user.password=str(123)
            db.session.add(user)
            db.session.commit()
            return True
        return False
    def to_json(self):
        json_user = {
            'role': self.role_id,
            'username': self.username,
            'gravatar_url': self.gravatar(size=18)
        }
        return json_user

    @staticmethod
    def insert_admin(email, username, password,):
        user = User(email=email, username=username, password=password,role_id=1,confirmed=True,coin=10000)
        db.session.add(user)
        db.session.commit()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == 'root@qq.com':
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                    self.email.encode('utf-8')).hexdigest()

    def gravatar(self, size=40, default='identicon', rating='g'):
        # if request.is_secure:
        #     url = 'https://secure.gravatar.com/avatar'
        # else:
        #     url = 'http://www.gravatar.com/avatar'  rating='g'
        if self.gravatar_url == None:
            url = 'https://cdn.v2ex.com/gravatar'
            hash = self.avatar_hash or hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
            return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
                url=url, hash=hash, size=size, default=default, rating=rating)
        return self.gravatar_url
    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)
    def is_loged(self):
        return True
class AnonymousUser(AnonymousUserMixin):
    def to_json(self):
        json_user = {
            'role': 0
        }
        return json_user

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False
    def is_loged(self):
        return False
login_manager.anonymous_user = AnonymousUser

# callback function for flask-login extentsion
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class ArticleType(db.Model):
    __tablename__ = 'articleTypes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    articles = db.relationship('Article', backref='articleType', lazy='dynamic')

    @staticmethod
    @cache.cached(timeout=60 * 5)
    def getalltypes():
        return [(t.id, t.name) for t in ArticleType.query.all()]

    @staticmethod
    @cache.memoize(50)
    def gettypename_byid(id):
        return ArticleType.query.get_or_404(id).name

    @staticmethod
    def insert_articleTypes():
        articleTypes = [u'驾校招生', u'教练招生', u'驾考租车', u'科二租车陪练', u'科三租车陪练']
        for name in articleTypes:
            articleType = ArticleType(name=name)
            db.session.add(articleType)
        db.session.commit()

    def __repr__(self):
        return '<Type %r>' % self.id


class DriverType(db.Model):
    __tablename__ = 'driverTypes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    articles = db.relationship('Article', backref='driverType', lazy='dynamic')

    @staticmethod
    def getall_drivertypes():
        return [(t.id, t.name) for t in DriverType.query.all()]

    @staticmethod
    def get_drivertypename_byid(id):
        return DriverType.query.get_or_404(id).name

    @staticmethod
    def insert_driverTypes():
        driverTypes = [u'C1', u'C2', u'驾考租车', u'科二租车陪练', u'科三租车陪练']
        for name in driverTypes:
            driverType = DriverType(name=name)
            db.session.add(driverType)
        db.session.commit()

    def __repr__(self):
        return '<DriverType %r>' % self.id


class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    city=db.Column(db.String(128))
    articleType_id = db.Column(db.Integer, db.ForeignKey('articleTypes.id'))
    callname=db.Column(db.String(32))
    tel=db.Column(db.String(32))
    detailplace=db.Column(db.String(128))
    title = db.Column(db.String(64))
    content = db.Column(db.Text)
    comname=db.Column(db.String(32))
    create_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), default=1)

    price = db.Column(db.String(32))
    driverType_id = db.Column(db.Integer, db.ForeignKey('driverTypes.id')) #c1
    can_comment = db.Column(db.Boolean,default=True)

    ip=db.Column(db.String(32))
    lng = db.Column(db.Float)
    lat = db.Column(db.Float)
    mprovince = db.Column(db.String(16))
    mcity = db.Column(db.String(16))

    def __init__(self, **kwargs):
        super(Article, self).__init__(**kwargs)
        if self.ip is not None:
            if self.ip=='127.0.0.1':
                self.ip = '36.63.43.63'
            if self.ip != '127.0.0.1':
                response = urllib2.urlopen('http://api.map.baidu.com/location/ip?ak=oq97zlCcVz70CqLvOGMIc7MwG3kvdynD&ip='+self.ip+'&coor=bd09ll')
                res = response.read()
                hjson = json.loads(res)
                self.lng = hjson['content']['point']['x']
                self.lat = hjson['content']['point']['y']
                self.mprovince = hjson['content']['address_detail']['province'][:-1]
                self.mcity = hjson['content']['address_detail']['city'][:-1]
    def __repr__(self):
        return '<Article %r>' % self.id

class Plugin(db.Model):
    __tablename__ = 'plugins'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=True)
    note = db.Column(db.Text, default='')
    content = db.Column(db.Text, default='')
    order = db.Column(db.Integer, default=0)
    disabled = db.Column(db.Boolean, default=False)

    def sort_delete(self):
        for plugin in Plugin.query.order_by(Plugin.order.asc()).offset(self.order).all():
            plugin.order -= 1
            db.session.add(plugin)

    @staticmethod
    def insert_system_plugin():
         plugin = Plugin(title=u'博客统计',note=u'系统插件',content='system_plugin',order=1)
         db.session.add(plugin)
         db.session.commit()

    def __repr__(self):
        return '<Plugin %r>' % self.title


class Js(db.Model):
    __tablename__ = 'js_code'
    id = db.Column(db.Integer, primary_key=True)
    js = db.Column(db.Text())
    @staticmethod
    def insert_js():
        js_code = Js(js="""<!-- 多说公共JS代码 start (一个网页只需插入一次) -->
<script type="text/javascript">
var duoshuoQuery = {short_name:"jiakaozuche"};
	(function() {
		var ds = document.createElement('script');
		ds.type = 'text/javascript';ds.async = true;
		ds.src = (document.location.protocol == 'https:' ? 'https:' : 'http:') + '//static.duoshuo.com/embed.js';
		ds.charset = 'UTF-8';
		(document.getElementsByTagName('head')[0]
		 || document.getElementsByTagName('body')[0]).appendChild(ds);
	})();
	</script>
<!-- 多说公共JS代码 end -->""")
        db.session.add(js_code)
        db.session.commit()
    def __repr__(self):
        return '<Js %r>' % self.id

