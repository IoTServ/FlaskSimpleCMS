#!/usr/bin/env python
from flask_script import Manager,Shell
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
from app.models import ArticleType,Article, Plugin, Role,User,Js,DriverType
from gevent.wsgi import WSGIServer

app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


# Global variables to jiajia2 environment:
app.jinja_env.globals['ArticleType'] = ArticleType
app.jinja_env.globals['Plugin'] = Plugin
app.jinja_env.globals['Article'] = Article
app.jinja_env.globals['Role'] = Role
app.jinja_env.globals['Js'] = Js
app.jinja_env.globals['DriverType'] = DriverType

def make_shell_context():
    return dict(db=db, ArticleType=ArticleType, Article=Article, User=User,Plugin=Plugin,Js=Js,DriverType=DriverType)

manager.add_command("shell", Shell(make_context=make_shell_context))

@manager.command
def deploy(deploy_type):
    from flask.ext.migrate import upgrade
    from app.models import User, \
        ArticleType, Plugin, Js, DriverType
    # upgrade database to the latest version
    upgrade()
    if deploy_type == 'product':
        Role.insert_roles()
        ArticleType.insert_articleTypes()
        # step_2:insert admin account
        User.insert_admin(email='root@qq.com', username='root', password='root')
        User.insert_admin(email='user@qq.com', username='user', password='user')
        Plugin.insert_system_plugin()
        Js.insert_js()
        DriverType.insert_driverTypes()
if __name__ == '__main__':
    #app.run('0.0.0.0', debug = True, port = 8000, ssl_context ='adhoc')
    #manager.run()
    ##http_server = WSGIServer(('0.0.0.0', 444), app, keyfile='214022688930279.key', certfile='214022688930279.pem')
    http_server = WSGIServer(('0.0.0.0', 8081), app)
    http_server.serve_forever()

