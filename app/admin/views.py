# coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from datetime import datetime
import json
from flask import render_template, redirect, flash, \
    url_for, request
from flask_login import login_required, current_user
from . import admin
from ..models import ArticleType, Article, User, Plugin , Js
from .forms import SubmitArticlesForm, ManageArticlesForm, DeleteArticleForm, \
    DeleteArticlesForm, SubmitJSForm, \
    AddBlogPluginForm, ChangePasswordForm, EditUserInfoForm, GiveCoinForm, QuxiaoRenlingForm, ReplaceEmailForm
from .. import db
from ..decorators import admin_required


@admin.route('/')
@login_required
@admin_required
def manager():
    return redirect(url_for('admin.account'))

@admin.route('/quxiao-renling', methods=['GET', 'POST'])
@login_required
@admin_required
def quxiaoRenling():
    form = QuxiaoRenlingForm()
    if form.validate_on_submit():
        id = int(form.id.data)
        article = Article.query.filter_by(id=id).first_or_404()
        article.author_id = 1
        db.session.add(article)
        db.session.commit()
        flash(u'取消认领' + form.id.data + '成功！', 'success')
        return redirect(url_for('admin.quxiaoRenling'))
    if form.errors:
        flash(u'取消认领失败！', 'danger')
    return render_template('admin/quxiao_renling.html', form=form)


@admin.route('/email-replace', methods=['GET', 'POST'])
@login_required
@admin_required
def emailReplace():
    form = ReplaceEmailForm()
    if form.validate_on_submit():
        old_email = form.old_email.data
        user = User.query.filter_by(email=old_email).first_or_404()
        user.email = form.new_email.data
        db.session.add(user)
        db.session.commit()
        flash(u'邮件置换' + form.old_email.data +'到'+form.new_email.data+ '成功！', 'success')
        return redirect(url_for('admin.emailReplace'))
    if form.errors:
        flash(u'置换失败', 'danger')
    return render_template('admin/email_tihuan.html', form=form)


@admin.route('/give-coin', methods=['GET', 'POST'])
@login_required
@admin_required
def giveCoin():
    form = GiveCoinForm()
    if form.validate_on_submit():
        id = int(form.id.data)
        user = User.query.filter_by(id=id).first_or_404()
        user.coin = user.coin+int(form.num.data)
        db.session.add(user)
        db.session.commit()
        flash(u'给予金币'+form.num.data+'成功！', 'success')
        return redirect(url_for('admin.giveCoin'))
    if form.errors:
        flash(u'给予失败', 'danger')
    return render_template('admin/give_coin.html', form=form)

@admin.route('/user-list')
@login_required
@admin_required
def userList():
    page = request.args.get('page', 1, type=int)

    pagination = User.query.order_by(User.sign_date.desc()).paginate(
        page, per_page=1500,
        error_out=False)
    users = pagination.items

    return render_template('admin/user_list.html',
                           User=User, pagination=pagination, endpoint='.userList',
                           users=users, page=page)

@admin.route('/custom/user-manage/baned/<int:id>')
@login_required
@admin_required
def disable_user(id):
    page = request.args.get('page', 1, type=int)

    user = User.query.get_or_404(id)
    user.banded = True
    db.session.add(user)
    db.session.commit()
    flash(u'用户禁用成功！', 'success')
    return redirect(url_for('admin.userList', page=page))


@admin.route('/custom/user-manage/no-baned/<int:id>')
@login_required
@admin_required
def enable_user(id):
    page = request.args.get('page', 1, type=int)

    user = User.query.get_or_404(id)
    user.banded = False
    db.session.add(user)
    db.session.commit()
    flash(u'启用用户成功！', 'success')
    return redirect(url_for('admin.userList', page=page))

@admin.route('/js', methods=['GET', 'POST'])
@login_required
@admin_required
def js():
    form = SubmitJSForm()
    query_js=Js.query.first()
    if form.validate_on_submit():
        js_code = form.js_code.data
        query_js.js=js_code
        db.session.add(query_js)
        db.session.commit()
        flash(u'更新成功！', 'success')
        return redirect(url_for('admin.js'))
    if form.errors:
        flash(u'发布失败', 'danger')
    form.js_code.data=query_js.js
    return render_template('admin/submit_js.html', form=form)

@admin.route('/submit-articles', methods=['GET', 'POST'])
@login_required
@admin_required
def submitArticles():
    form = SubmitArticlesForm()
    types = ArticleType.getalltypes()
    form.types.choices = types

    if form.validate_on_submit():
        area =form.area.data
        type_id =form.types.data
        callname =form.callname.data
        tel = form.tel.data
        addr = form.addr.data
        title = form.title.data
        content = form.content.data
        comname = form.comname.data
        articleType = ArticleType.query.get(type_id)
        if articleType:
            article = Article(city = area,callname =callname,tel = tel,detailplace = addr,title = title,
                              content = content,comname = comname,articleType=articleType,author=current_user,can_comment=True,update_time=datetime.utcnow())
            db.session.add(article)
            db.session.commit()
            article_id = article.id
            return redirect(url_for('main.articleDetails', id=article_id))
    if form.errors:
        flash(u'发表失败', 'danger')

    return render_template('admin/submit_articles.html', form=form)


@admin.route('/edit-articles/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editArticles(id):
    article = Article.query.get_or_404(id)
    form = SubmitArticlesForm()
    types = ArticleType.getalltypes()
    form.types.choices = types
    if form.validate_on_submit():
        articleType = ArticleType.query.get_or_404(int(form.types.data))
        article.articleType = articleType
        article.area = form.area.data
        article.type_id = form.types.data
        article.callname = form.callname.data
        article.tel = form.tel.data
        article.addr = form.addr.data
        article.title = form.title.data
        article.content = form.content.data
        article.comname = form.comname.data
        article.update_time = datetime.utcnow()
        db.session.add(article)
        db.session.commit()
        flash(u'更新成功！', 'success')
        return redirect(url_for('main.articleDetails', id=article.id))
    form.area.data = article.city
    form.types.data = article.articleType_id
    form.callname.data = article.callname
    form.tel.data = article.tel
    form.addr.data = article.detailplace
    form.title.data = article.title
    form.content.data = article.content
    form.comname.data = article.comname
    return render_template('admin/edit_articles.html', form=form)


@admin.route('/manage-articles', methods=['GET', 'POST'])
@login_required
@admin_required
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

        result = Article.query.filter_by(author=current_user).order_by(Article.update_time.desc())
        if types_id != -1:
            articleType = ArticleType.query.get_or_404(types_id)
            result = result.filter_by(articleType=articleType).order_by(Article.update_time.desc())
        pagination_search = result.paginate(
                page, per_page=500, error_out=False)
    if pagination_search != 0:
        pagination = pagination_search
        articles = pagination_search.items
    else:
        page = request.args.get('page', 1, type=int)
        pagination = Article.query.order_by(Article.update_time.desc()).paginate(
                page, per_page=500,
                error_out=False)
        articles = pagination.items
    return render_template('admin/manage_articles.html', Article=Article,
                           articles=articles, pagination=pagination,
                           endpoint='admin.manage_articles',
                           form=form, form2=form2, form3=from3,
                           types_id=types_id, page=page)


@admin.route('/manage-articles/delete-article', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_article():
    types_id = request.args.get('types_id', -1, type=int)
    form = DeleteArticleForm()

    if form.validate_on_submit():
        articleId = int(form.articleId.data)
        article = Article.query.get_or_404(articleId)
        db.session.delete(article)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash(u'删除失败！', 'danger')
        else:
            flash(u'成功删除！' , 'success')
    if form.errors:
        flash(u'删除失败！', 'danger')

    return redirect(url_for('admin.manage_articles', types_id=types_id,
                            page=request.args.get('page', 1, type=int)))


@admin.route('/manage-articles/delete-articles', methods=['GET', 'POST'])
@login_required
@admin_required
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
            article = Article.query.get_or_404(int(articleId))
            db.session.delete(article)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash(u'删除失败！', 'danger')
        else:
            flash(u'成功删除！' , 'success')
    if form.errors:
        flash(u'删除失败！', 'danger')

    return redirect(url_for('admin.manage_articles', types_id=types_id,
                            page=request.args.get('page', 1, type=int)))



@admin.route('/custom/blog-plugin', methods=['GET', 'POST'])
@login_required
@admin_required
def custom_blog_plugin():
    page = request.args.get('page', 1, type=int)

    pagination = Plugin.query.order_by(Plugin.order.asc()).paginate(
            page, per_page=15,
            error_out=False)
    plugins = pagination.items

    return render_template('admin/custom_blog_plugin.html',
                           Plugin=Plugin, pagination=pagination, endpoint='.custom_blog_plugin',
                           plugins=plugins, page=page)


@admin.route('/custom/blog-plugin/delete/<int:id>')
@login_required
@admin_required
def delete_plugin(id):
    page = request.args.get('page', 1, type=int)

    plugin = Plugin.query.get_or_404(id)
    plugin.sort_delete()
    db.session.delete(plugin)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash(u'删除插件失败！', 'danger')
    else:
        flash(u'删除插件成功！' ,'success')
    return redirect(url_for('admin.custom_blog_plugin', page=page))


@admin.route('/custom/blog-plugin/sort-up/<int:id>')
@login_required
@admin_required
def plugin_sort_up(id):
    page = request.args.get('page', 1, type=int)

    plugin = Plugin.query.get_or_404(id)
    pre_plugin = Plugin.query.filter_by(order=plugin.order-1).first()
    if pre_plugin:
        (plugin.order, pre_plugin.order) = (pre_plugin.order, plugin.order)
        db.session.add(plugin)
        db.session.add(pre_plugin)
        db.session.commit()
        flash(u'成功将该插件升序！', 'success')
    else:
        flash(u'该插件已经位于最前面！', 'danger')
    return redirect(url_for('admin.custom_blog_plugin', page=page))


@admin.route('/custom/blog-plugin/sort-down/<int:id>')
@login_required
@admin_required
def plugin_sort_down(id):
    page = request.args.get('page', 1, type=int)

    plugin = Plugin.query.get_or_404(id)
    latter_plugin = Plugin.query.filter_by(order=plugin.order+1).first()
    if latter_plugin:
        (latter_plugin.order, plugin.order) = (plugin.order, latter_plugin.order)
        db.session.add(plugin)
        db.session.add(latter_plugin)
        db.session.commit()
        flash(u'成功将该插件降序！', 'success')
    else:
        flash(u'该插件已经位于最后面！', 'danger')
    return redirect(url_for('admin.custom_blog_plugin', page=page))


@admin.route('/custom/blog-plugin/disable/<int:id>')
@login_required
@admin_required
def disable_plugin(id):
    page = request.args.get('page', 1, type=int)

    plugin = Plugin.query.get_or_404(id)
    plugin.disabled = True
    db.session.add(plugin)
    db.session.commit()
    flash(u'禁用插件成功！', 'success')
    return redirect(url_for('admin.custom_blog_plugin', page=page))


@admin.route('/custom/blog-plugin/enable/<int:id>')
@login_required
@admin_required
def enable_plugin(id):
    page = request.args.get('page', 1, type=int)

    plugin = Plugin.query.get_or_404(id)
    plugin.disabled = False
    db.session.add(plugin)
    db.session.commit()
    flash(u'启用插件成功！', 'success')
    return redirect(url_for('admin.custom_blog_plugin', page=page))


@admin.route('/custom/blog-plugin/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_plugin():
    form = AddBlogPluginForm()

    if form.validate_on_submit():
        title = form.title.data
        plugin = Plugin.query.filter_by(title=title).first()
        if plugin:
            form = AddBlogPluginForm(title=title, note=form.note.data,
                                     content=form.content.data)
            flash(u'添加插件失败！该插件名称已经存在。', 'danger')
            return render_template('admin/blog_plugin_add.html', form=form)
        else:
            note = form.note.data
            content = form.content.data
            plugin_count = Plugin.query.count()
            plugin = Plugin(title=title, note=note,
                            content=content, order=plugin_count+1)
            db.session.add(plugin)
            db.session.commit()
            flash(u'添加插件成功！', 'success')
        return redirect(url_for('admin.custom_blog_plugin'))

    return render_template('admin/blog_plugin_add.html', form=form)


@admin.route('/custom/blog-plugin/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_plugin(id):
    page = request.args.get('page', 1, type=int)
    plugin = Plugin.query.get_or_404(id)
    form = AddBlogPluginForm(title=plugin.title,
                             note=plugin.note,
                             content=plugin.content)
    if form.validate_on_submit():
        title = form.title.data
        plugin_check = Plugin.query.filter_by(title=title).first()
        if plugin_check and plugin_check.id != id:
            flash(u'修改插件失败！该插件名称已经存在。', 'danger')
            return redirect(url_for('admin.edit_plugin', id=id))
        else:
            plugin.title = title
            plugin.note = form.note.data
            plugin.content = form.content.data
            db.session.add(plugin)
            db.session.commit()
            flash(u'修改插件成功！', 'success')
        return redirect(url_for('admin.custom_blog_plugin', page=page))

    return render_template('admin/blog_plugin_add.html', form=form, page=page)


@admin.route('/account/')
@login_required
@admin_required
def account():
    form = ChangePasswordForm()
    form2 = EditUserInfoForm()

    return render_template('admin/admin_account.html',
                           form=form, form2=form2)


@admin.route('/duoshuo/')
@login_required
@admin_required
def duoshuo():
    return render_template('admin/admin_duoshuo.html')



@admin.route('/account/change-password', methods=['GET', 'POST'])
@login_required
@admin_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash(u'修改密码成功！', 'success')
            return redirect(url_for('admin.account'))
        else:
            flash(u'修改密码失败！密码不正确！', 'danger')
            return redirect(url_for('admin.account'))


@admin.route('/account/edit-user-info', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user_info():
    form2 = EditUserInfoForm()

    if form2.validate_on_submit():
        if current_user.verify_password(form2.password.data):
            current_user.username = form2.username.data
            current_user.email = form2.email.data
            db.session.add(current_user)
            db.session.commit()
            flash(u'修改用户信息成功！', 'success')
            return redirect(url_for('admin.account'))
        else:
            flash(u'修改用户信息失败！密码不正确！', 'danger')
            return redirect(url_for('admin.account'))
