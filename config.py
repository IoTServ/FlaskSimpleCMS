# coding: utf-8
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    #邮件设置
    MAIL_SERVER = 'smtpdm.aliyun.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'notice@iotserv.com'
    MAIL_PASSWORD = '*'
    MAIL_SUBJECT_PREFIX = u'WebSite'
    MAIL_SENDER = u'驾考租车网 <notice@jiakaozuche.com>'
    #初始化coin设置
    COIN_REGISTER_GET = 5
    COIN_SIGN_GET = 1
    COIN_RENLING = 2
    COIN_SUBMIT_COST = 2
    COIN_NOT_COMENT_COST = 100
    COIN_VIP = 30

    CACHE_TYPE = 'simple'
    #分页设置
    ARTICLES_PER_PAGE = 10
    SITEMAP_PER_PAGE = 1000
    #CACHE_TYPE='redis'
    #CACHE_REDIS_HOST='127.0.0.1'
    #CACHE_REDIS_PORT=6379
    #CACHE_REDIS_DB=''
    #CACHE_REDIS_PASSWORD=''
    # DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_POOL_SIZE = 50
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:root@localhost/car'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SECRET_KEY = 'secret'
    WTF_CSRF_SECRET_KEY = 'randomt@key' # for csrf protection

    BUCKET_KEY = ''
    BUCKET_VALUE = ''
    BUCKET_URL = ''
    BUCKET_NAME = ''

    @staticmethod
    def init_app(app):
        pass