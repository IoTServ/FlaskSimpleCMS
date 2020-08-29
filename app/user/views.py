# coding:utf-8
import sys, time, os

reload(sys)
sys.setdefaultencoding('utf-8')
import json,oss2,bleach
from flask import render_template, redirect, flash, \
    url_for, request, current_app, jsonify
from flask_login import login_required, current_user
from . import user
from ..models import ArticleType, Article, User, DriverType
from .forms import SubmitArticlesForm, ManageArticlesForm, DeleteArticleForm, \
    DeleteArticlesForm, GravatarForm, \
    ChangePasswordForm, EditUserInfoForm
from .. import db
from datetime import datetime
from werkzeug.utils import secure_filename
from ..email import send_email

tags = ['font', 'span', 'div', 'table', 'td', 'th', 'a', 'img', 'p', 'ol' ,'ul', 'li',
 'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'hr', 'br','tbody','tr','strong',
 'b','sub','sup','em','i','u','strike','s','del']
attrs = {
        '*': ['style','align','class'],
        'font' : ['color', 'size', 'face'],
        'table': ['border', 'cellspacing', 'cellpadding', 'width', 'height', 'bordercolor'],
        'td': ['valign', 'width', 'height', 'colspan', 'rowspan', 'bgcolor'],
        'th': ['valign', 'width', 'height', 'colspan', 'rowspan', 'bgcolor'],
        'a' : ['href', 'target', 'name'],
        'img' : ['src', 'width', 'height', 'border', 'alt', 'title']
}
styles = ['background-color', 'color', 'font-size', 'font-family', 'background',
                'font-weight', 'font-style', 'text-decoration', 'vertical-align',
                'line-height','border', 'margin', 'padding', 'text-align',
                'margin-left', 'bgcolor', 'width', 'height', 'border-collapse',
                'text-indent', 'page-break-after']

@user.route('/upload', methods=['POST'])
@login_required
def upload():
    f = request.files['upload']
    fname = secure_filename(f.filename)  # 获取一个安全的文件名，且仅仅支持ascii字符；
    if os.path.splitext(fname)[1] not in ['.png', '.gif', '.jpg', '.JPG', '.jpeg', '.bmp']:
        flash(u'请上传png,gif,jpg,JPG,jpeg,bmp格式图片！', 'danger')
        return redirect(url_for('user.account'))
    time_format = str(time.strftime("%Y-%m-%d-%H%M%S", time.localtime()))

    auth = oss2.Auth('jdqYTE3dWkj3xE71', 'bZioe6E66oiJowsSVQOfS164JrBSVg ')
    bucket = oss2.Bucket(auth, 'http://oss-cn-hangzhou.aliyuncs.com', 'jiakaozuche')
    bucket.put_object(time_format + fname, f)
    #f.save('app/static/up/' + time_format + fname)
    #current_user.gravatar_url = '/static/up/' + time_format + fname
    current_user.gravatar_url = 'https://jiakaozuche.oss-cn-hangzhou.aliyuncs.com/' + time_format + fname+'-touxiang'
    db.session.add(current_user)
    db.session.commit()
    flash(u'更改头像成功！', 'success')
    return redirect(url_for('user.account'))


@user.route('/')
@login_required
def manager():
    return redirect(url_for('user.account'))


@user.route('/ren-ling/<int:id>')
@login_required
def reclaim(id):
    if current_user.coin < current_app.config['COIN_RENLING']:
        flash(u'您的金币不足！', 'danger')
        return redirect(url_for('user.account'))
    article = Article.query.get_or_404(id)
    if article.author_id!=1:
        flash(u'该信息已经被认领！如被冒领请联系站长。', 'danger')
        return redirect(url_for('user.account'))
    article.author=current_user
    current_user.coin=current_user.coin-current_app.config['COIN_RENLING']
    db.session.add(article)
    db.session.add(current_user)
    db.session.commit()
    flash(u'认领成功！', 'success')
    return redirect(url_for('user.account'))


@user.route('/sign')
@login_required
def sign():
    if current_user.sign_date != datetime.today().date():
        current_user.sign_date = datetime.today()
        db.session.add(current_user)
        db.session.commit()
        current_user.coin = current_user.coin + current_app.config['COIN_SIGN_GET']
        db.session.add(current_user)
        db.session.commit()
        flash(u'签到成功！', 'success')
        return redirect(url_for('user.account'))
    flash(u'签到失败！今天已经签到过！', 'danger')
    return redirect(url_for('user.account'))


@user.route('/submit-articles', methods=['GET', 'POST'])
@login_required
def submitArticles():
    form = SubmitArticlesForm()

    types = ArticleType.getalltypes()
    drivertypes = DriverType.getall_drivertypes()
    form.types.choices = types
    form.drivertypes.choices = drivertypes

    if form.validate_on_submit():

        area = form.area.data
        type_id = form.types.data

        drivertype_id = form.drivertypes.data
        price = form.price.data

        callname = form.callname.data
        tel = form.tel.data
        addr = form.addr.data
        title = form.title.data
        content = form.content.data
        comname = form.comname.data
        if current_user.coin < 5:
            flash(u'您的金币不足！', 'danger')
            return redirect(url_for('user.submitArticles'))
        current_user.coin = current_user.coin - 5
        db.session.add(current_user)
        db.session.commit()
        ip = form.ip.data
        if type_id and drivertype_id:
            article = Article(ip=ip)
            article.city = area
            article.callname = callname
            article.tel = tel
            article.detailplace = addr
            article.title = title
            article.content = bleach.clean(content,tags = tags,attributes = attrs,styles = styles)
            article.comname = comname
            article.articleType_id = type_id
            article.driverType_id = drivertype_id
            article.price = price
            article.author = current_user
            article.mprovince = form.province.data
            article.mcity = form.city.data
            db.session.add(article)
            db.session.commit()
            flash(u'发表成功！', 'success')
            article_id = article.id
            return redirect(url_for('user.editArticles', id=article_id))
    if form.errors:
        flash(u'发表失败', 'danger')

    return render_template('user/submit_articles.html', form=form)


@user.route('/edit-articles/<int:id>', methods=['GET', 'POST'])
@login_required
def editArticles(id):
    if Article.query.get_or_404(id).author != current_user:
        flash(u'对不起！您对该文章没有编辑权限！', 'danger')
        return redirect(url_for('main.index'))
    article = Article.query.get_or_404(id)
    form = SubmitArticlesForm()
    types = ArticleType.getalltypes()
    drivertypes = DriverType.getall_drivertypes()
    form.types.choices = types
    form.drivertypes.choices = drivertypes
    ip = request.remote_addr
    if form.validate_on_submit():
        #articleType = ArticleType.query.get_or_404(int(form.types.data))
        article.articleType_id = form.types.data
        article.driverType_id = form.drivertypes.data
        article.price = form.price.data
        article.city = form.area.data
        article.type_id = form.types.data
        article.callname = form.callname.data
        article.tel = form.tel.data
        article.detailplace = form.addr.data
        article.title = form.title.data
        article.content = bleach.clean(form.content.data,tags = tags,attributes = attrs,styles = styles)
        article.comname = form.comname.data
        article.update_time = datetime.utcnow()
        article.ip = form.ip.data
        db.session.add(article)
        db.session.commit()
        flash(u'更新成功！', 'success')
        return redirect(url_for('user.editArticles', id=article.id))
    form.area.data = article.city
    form.types.data = article.articleType_id
    form.drivertypes.data = article.driverType_id
    form.price.data = article.price
    form.callname.data = article.callname
    form.tel.data = article.tel
    form.addr.data = article.detailplace
    form.title.data = article.title
    form.content.data = article.content
    form.comname.data = article.comname
    return render_template('user/edit_articles.html', form=form)


@user.route('/manage-articles', methods=['GET', 'POST'])
@login_required
def manage_articles():
    types_id = request.args.get('types_id', -1, type=int)
    form = ManageArticlesForm(request.form, types=types_id)
    form2 = DeleteArticleForm()  # for delete an article
    from3 = DeleteArticlesForm()  # for delete articles

    types = ArticleType.getalltypes()
    types.append((-1, u'全部分类'))
    form.types.choices = types

    pagination_search = 0

    if form.validate_on_submit() or \
            (request.args.get('types_id') is not None):
        if form.validate_on_submit():
            types_id = form.types.data
            page = 1
        else:
            types_id = request.args.get('types_id', type=int)
            form.types.data = types_id
            page = request.args.get('page', 1, type=int)

        result = Article.query.filter_by(author=current_user).order_by(Article.create_time.desc())
        if types_id != -1:
            articleType = ArticleType.query.get_or_404(types_id)
            result = result.filter_by(articleType=articleType)
        pagination_search = result.paginate(
            page, per_page=20, error_out=False)

    if pagination_search != 0:
        pagination = pagination_search
        articles = pagination_search.items
    else:
        page = request.args.get('page', 1, type=int)
        pagination = Article.query.filter_by(author=current_user).order_by(Article.create_time.desc()).paginate(
            page, per_page=20,
            error_out=False)
        articles = pagination.items

    return render_template('user/manage_articles.html', Article=Article,
                           articles=articles, pagination=pagination,
                           endpoint='user.manage_articles',
                           form=form, form2=form2, form3=from3,
                           types_id=types_id, page=page)


@user.route('/manage-articles/delete-article', methods=['GET', 'POST'])
@login_required
def delete_article():
    types_id = request.args.get('types_id', -1, type=int)
    form = DeleteArticleForm()

    if form.validate_on_submit():
        articleId = int(form.articleId.data)
        if Article.query.get_or_404(articleId).author != current_user:
            flash(u'对不起！您对该文章没有删除权限！', 'danger')
            return redirect(url_for('main.index'))
        article = Article.query.get_or_404(articleId)
        db.session.delete(article)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash(u'删除失败！', 'danger')
        else:
            flash(u'成功删除！', 'success')
    if form.errors:
        flash(u'删除失败！', 'danger')

    return redirect(url_for('user.manage_articles', types_id=types_id,
                            page=request.args.get('page', 1, type=int)))


@user.route('/manage-articles/delete-articles', methods=['GET', 'POST'])
@login_required
def delete_articles():
    types_id = request.args.get('types_id', -1, type=int)
    # form2 = DeleteArticleForm()
    form = DeleteArticlesForm()

    # if form2.validate_on_submit():
    #     articleId = form2.articleId.data
    #     print articleId

    if form.validate_on_submit():
        articleIds = json.loads(form.articleIds.data)
        for articleId in articleIds:
            if Article.query.get_or_404(articleId).author != current_user:
                flash(u'对不起！您对该文章没有删除权限！', 'danger')
                return redirect(url_for('main.index'))
            article = Article.query.get_or_404(int(articleId))
            db.session.delete(article)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash(u'删除失败！', 'danger')
        else:
            flash(u'成功删除！', 'success')
    if form.errors:
        flash(u'删除失败！', 'danger')

    return redirect(url_for('user.manage_articles', types_id=types_id,
                            page=request.args.get('page', 1, type=int)))


@user.route('/account/')
@login_required
def account():
    form = ChangePasswordForm()
    form2 = EditUserInfoForm()
    form3 = GravatarForm()

    return render_template('user/admin_account.html',
                           form=form, form2=form2, form3=form3)


@user.route('/account/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash(u'修改密码成功！', 'success')
            return redirect(url_for('user.account'))
        else:
            flash(u'修改密码失败！密码不正确！', 'danger')
            return redirect(url_for('user.account'))


@user.route('/account/edit-user-info', methods=['GET', 'POST'])
@login_required
def edit_user_info():
    form2 = EditUserInfoForm()

    if form2.validate_on_submit():
        if form2.email.data is None or form2.username.data is None:
            flash(u'邮件或昵称不应为空！', 'danger')
            return redirect(url_for('user.account'))

        if current_user.verify_password(form2.password.data):
            if current_user.email != form2.email.data:
                if User.query.filter_by(email=form2.email.data).first():
                    flash(u'该邮件地址已经被使用！', 'danger')
                    return redirect(url_for('user.account'))
                token = current_user.generate_confirmation_token()
                send_email(current_user.email, u'确认您的账户',
                           'auth/email/confirm', user=current_user, token=token)
                current_user.confirmed = False
                flash(u'修改用户信息成功！请重新查看' + current_user.email + u'邮箱确认邮件，请查收邮件。', 'success')
            current_user.username = form2.username.data
            current_user.qq = form2.qq.data
            current_user.tel = form2.tel.data
            current_user.wechat = form2.wechat.data
            current_user.com_name = form2.comname.data
            current_user.email = form2.email.data
            db.session.add(current_user)
            db.session.commit()
            return redirect(url_for('user.account'))
        else:
            flash(u'修改用户信息失败！密码不正确！', 'danger')
            return redirect(url_for('user.account'))
    if form2.errors:
        flash(u'更新失败！', 'danger')
        return redirect(url_for('user.account'))
