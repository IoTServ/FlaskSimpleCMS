#coding:utf-8
import os,json,time,oss2

from datetime import datetime,timedelta
from flask import make_response,send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from flask import render_template, request, current_app,flash,redirect,url_for
from . import main
from ..models import Article, ArticleType,User
from .. import csrf, cache


@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.order_by(Article.update_time.desc()).paginate(
            page, per_page=current_app.config['ARTICLES_PER_PAGE'],
            error_out=False)
    articles = pagination.items
    return render_template('index.html', articles=articles,
                           pagination=pagination, endpoint='.index',page=page)

@main.route('/robots.txt')
def robots():
    return send_file('templates/robots.txt',mimetype='text/plain',cache_timeout=0)

# a route for generating sitemap.xml
@main.route('/sitemap.xml', methods=['GET'])
def sitemap_static():
    article_sitemap_num=Article.query.count()/1000 + 2
    user_sitemap_num = User.query.count()/1000 + 2
    sitemap_xml = render_template('sitemap.xml',time=datetime.utcnow().date(),article_sitemap_num=article_sitemap_num,user_sitemap_num=user_sitemap_num)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response


@main.route('/sitemap-<int:page>.xml', methods=['GET'])
def sitemap(page):
    """Generate sitemap.xml. Makes a list of urls and date modified."""
    pages = []
    # Article model pages
    articles = Article.query.order_by(Article.update_time).paginate(page, per_page=current_app.config['SITEMAP_PER_PAGE'],error_out=False).items
    for article in articles:
        url = url_for('main.articleDetails', id=article.id, _external=True)
        time=article.update_time or datetime(2017, 1, 1)
        modified_time = time.date().isoformat()
        pages.append([url, modified_time])

    sitemap_xml = render_template('article-sitemap.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response

@main.route('/urls-<int:page>.txt', methods=['GET'])
def urls(page):
    """Generate sitemap.xml. Makes a list of urls and date modified."""
    pages = []
    # Article model pages
    articles = Article.query.order_by(Article.update_time).paginate(page, per_page=2000,error_out=False).items
    for article in articles:
        url = url_for('mip.miparticleDetails', id=article.id, _external=True)
        time=article.update_time or datetime(2017, 1, 1)
        modified_time = time.date().isoformat()
        pages.append([url, modified_time])

    sitemap_txt = render_template('urls.txt', pages=pages)
    response = make_response(sitemap_txt)
    response.headers["Content-Type"] = "text/plain"

    return response

@main.route('/user-<int:page>.xml', methods=['GET'])
def user_sitemap(page):
    """Generate sitemap.xml. Makes a list of urls and date modified."""
    pages = []
    # Article model pages
    users = User.query.filter_by(confirmed=True,banded=False).paginate(page, per_page=current_app.config['SITEMAP_PER_PAGE'],error_out=False).items
    for user in users:
        url = url_for('username.detials', id=user.id, _external=True)
        pages.append([url])
    sitemap_xml = render_template('user-sitemap.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response

@main.route('/place')
def place():
    return render_template('moreplace.html')

@main.route('/search/<word>', methods=['POST','GET'])
def search(word):
    page = request.args.get('page', 1, type=int)
    articles=Article.query.filter(Article.detailplace.like('%'+word+'%')).order_by(Article.update_time.desc())
    if articles.count()==0 and len(word)>4:
        flash(u'抱歉没有找到您搜索的相关地址的结果。', 'danger')
        return redirect(url_for('main.index'))
    pagination = articles.paginate(
            page, per_page=current_app.config['ARTICLES_PER_PAGE'],
            error_out=False)
    articles = pagination.items
    return render_template('search.html', articles=articles,
                           pagination=pagination, endpoint='.search',page=page,word=word)

@main.route('/city/<word>', methods=['POST','GET'])
def city(word):
    page = request.args.get('page', 1, type=int)
    articles=Article.query.filter(Article.city.like('%'+word+'%')).order_by(Article.update_time.desc())
    if articles.count()==0 and len(word)>4:
        flash(u'抱歉没有找到您搜索的相关地址的结果。', 'danger')
        return redirect(url_for('main.index'))
    pagination = articles.paginate(
            page, per_page=current_app.config['ARTICLES_PER_PAGE'],
            error_out=False)
    articles = pagination.items
    return render_template('city.html', articles=articles,
                           pagination=pagination, endpoint='.city',page=page,word=word)

@main.route('/jiakao/<int:id>/')
def articleTypes(id):
    page = request.args.get('page', 1, type=int)
    name = ArticleType.gettypename_byid(id)
    pagination = ArticleType.query.get_or_404(id).articles.order_by(Article.update_time.desc()).paginate(page, per_page=current_app.config['ARTICLES_PER_PAGE'],error_out=False)
    articles = pagination.items
    return render_template('jiakao.html', articles=articles,
                           pagination=pagination, endpoint='.articleTypes',
                           id=id,name=name,page=page)


@main.route('/jiaxiao-peilian/jiakao-<int:id>.html')
def articleDetails(id):
    article = Article.query.get_or_404(id)
    #article = Article.query.filter(Article.title.like('%35%')).first()
    return render_template('article_detials.html', article=article,id=article.id)
    # page=page, this is used to return the current page args to the
    # disable comment or enable comment endpoint to pass it to the articleDetails endpoint

@csrf.exempt
@main.route('/upload', methods=['POST'])
@login_required
def upload():
    dict_tmp = {}
    f = request.files['imgFile']
    dir = request.args.get('dir')
    if dir == 'image':
        if os.path.splitext(f.filename)[1] not in ['.png','.gif', '.jpg','.JPG', '.jpeg', '.bmp']:
            dict_tmp['error'] = 1
            dict_tmp['message'] = "保存出错！文件扩展名只能是：png,gif, jpg, jpeg, bmp"
            return json.dumps(dict_tmp)
        else:
            fname = secure_filename(f.filename)  # 获取一个安全的文件名，且仅仅支持ascii字符；
            time_format = str(time.strftime("%Y-%m-%d-%H%M%S", time.localtime()))
            try:
                # f.save('app/static/up/'+time_format+fname)
                app = current_app._get_current_object()
                auth = oss2.Auth(app.config['BUCKET_KEY'], app.config['BUCKET_VALUE'])
                bucket = oss2.Bucket(auth, app.config['BUCKET_URL'], app.config['BUCKET_NAME'])
                bucket.put_object(time_format + fname, f)
            except:
                dict_tmp['error'] = 1  # 成功{ "error":0, "url": "/static/image/filename"}
                dict_tmp['message'] = "保存出错！"
                return json.dumps(dict_tmp)
            dict_tmp['error'] = 0  # 成功{ "error":0, "url": "/static/image/filename"}
            # dict_tmp['url'] = "/static/up/"+time_format+fname
            dict_tmp['url'] = "https://jiakaozuche.oss-cn-hangzhou.aliyuncs.com/" + time_format + fname + '-content'
            return json.dumps(dict_tmp)
    dict_tmp['error'] = 1
    dict_tmp['message'] = "保存出错！"
    return json.dumps(dict_tmp)