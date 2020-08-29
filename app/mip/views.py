#coding:utf-8
import os,json,time,oss2

from datetime import datetime,timedelta
from flask import make_response,send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from flask import render_template, request, current_app,flash,redirect,url_for
from . import mip
from ..models import Article, ArticleType,User
from .. import csrf, cache

#MIP
@mip.route('/')
def mipindex():
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.order_by(Article.update_time.desc()).paginate(
            page, per_page=current_app.config['ARTICLES_PER_PAGE'],
            error_out=False)
    articles = pagination.items
    return render_template('mip/mipindex.html', articles=articles,
                           pagination=pagination, endpoint='.mipindex',page=page)

@mip.route('/place')
def mipplace():
    return render_template('mip/moreplace.html')

@mip.route('/jiaxiao-peilian/jiakao-<int:id>.html')
def miparticleDetails(id):
    article = Article.query.get_or_404(id)
    #article = Article.query.filter(Article.title.like('%35%')).first()
    return render_template('mip/article.html', article=article,id=article.id)
    # page=page, this is used to return the current page args to the
    # disable comment or enable comment endpoint to pass it to the articleDetails endpoint

###

@mip.route('/search/<word>', methods=['POST','GET'])
def mipsearch(word):
    page = request.args.get('page', 1, type=int)
    articles=Article.query.filter(Article.detailplace.like('%'+word+'%')).order_by(Article.update_time.desc())
    if articles.count()==0 and len(word)>4:
        flash(u'抱歉没有找到您搜索的相关地址的结果。', 'danger')
        return redirect(url_for('main.index'))
    pagination = articles.paginate(
            page, per_page=current_app.config['ARTICLES_PER_PAGE'],
            error_out=False)
    articles = pagination.items
    return render_template('mip/search.html', articles=articles,
                           pagination=pagination, endpoint='.mipsearch',page=page,word=word)

@mip.route('/city/<word>', methods=['POST','GET'])
def mipcity(word):
    page = request.args.get('page', 1, type=int)
    articles=Article.query.filter(Article.city.like('%'+word+'%')).order_by(Article.update_time.desc())
    if articles.count()==0 and len(word)>4:
        flash(u'抱歉没有找到您搜索的相关地址的结果。', 'danger')
        return redirect(url_for('mip.mipindex'))
    pagination = articles.paginate(
            page, per_page=current_app.config['ARTICLES_PER_PAGE'],
            error_out=False)
    articles = pagination.items
    return render_template('mip/city.html', articles=articles,
                           pagination=pagination, endpoint='.mipcity',page=page,word=word)

@mip.route('/jiakao/<int:id>/')
def miparticleTypes(id):
    page = request.args.get('page', 1, type=int)
    name = ArticleType.gettypename_byid(id)
    pagination = ArticleType.query.get_or_404(id).articles.order_by(Article.update_time.desc()).paginate(page, per_page=current_app.config['ARTICLES_PER_PAGE'],error_out=False)
    articles = pagination.items
    return render_template('mip/jiakao.html', articles=articles,
                           pagination=pagination, endpoint='.miparticleTypes',
                           id=id,name=name,page=page)

#MIP ENDSS