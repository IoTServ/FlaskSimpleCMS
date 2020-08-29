# coding:utf-8
from flask import render_template, session, make_response, request, url_for, flash,current_app
from flask_login import login_user, login_required, logout_user
from flask_login import current_user
from . import auth
from ..models import User
from .forms import LoginForm,RegisterForm,RepasswordForm
from .. import db
from flask import redirect
from flask import request
from ..email import send_email
from ..geetest import GeetestLib

pc_geetest_id = "8854fee6404ce673bbe30c"
pc_geetest_key = "bb8a71d97a9ec"

@auth.route('/reg_str', methods=["GET"])
def get_pc_captcha():
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process()
    session[gt.GT_STATUS_SESSION_KEY] = status
    response_str = gt.get_response_str()
    return response_str

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_loged():
        flash(u'您已经处于登录状态！', 'danger')
        return redirect(url_for('main.index'))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            flash(u'登陆成功！欢迎回来，%s!' % user.username, 'success')
            return redirect(url_for('main.index'))
        else:
            flash(u'登陆失败！用户名或密码错误，请重新登陆。', 'danger')
    if form.errors:
        flash(u'登陆失败，请尝试重新登陆.', 'danger')

    return render_template('auth/login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if current_user.is_loged():
        return redirect(url_for('main.index'))

    if form.validate_on_submit():
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.form[gt.FN_CHALLENGE]
        validate = request.form[gt.FN_VALIDATE]
        seccode = request.form[gt.FN_SECCODE]
        status = session[gt.GT_STATUS_SESSION_KEY]
        if status:
            result = gt.success_validate(challenge, validate, seccode)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            if User.query.filter_by(email=form.email.data).first():
                flash(u'该邮件地址已经被注册！', 'danger')
                return redirect(url_for('auth.register'))
            user = User(email=form.email.data,initial_email=form.email.data,qq=form.qq.data,tel=form.tel.data,wechat=form.wechat.data,
                        com_name=form.comname.data,username=form.username.data,password=form.password.data,coin=current_app.config['COIN_REGISTER_GET'])
            db.session.add(user)
            db.session.commit()
            login_user(user)

            token = user.generate_confirmation_token()
            send_email(user.email, u'确认您的账户',
                       'auth/email/confirm', user=user, token=token)
            flash(u'邮件已经发送到您的邮箱：'+user.email+u'请登录查看邮件，并点击链接确认！','success')

            return redirect(url_for('user.account'))
    if form.errors:
        flash(u'注册失败，请检查，尝试重新注册.', 'danger')

    return render_template('auth/register.html', form=form)

@auth.route('/repassword', methods=['GET', 'POST'])
def repassword():
    form = RepasswordForm()
    if current_user.is_loged():
        return redirect(url_for('main.index'))

    if form.validate_on_submit():
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.form[gt.FN_CHALLENGE]
        validate = request.form[gt.FN_VALIDATE]
        seccode = request.form[gt.FN_SECCODE]
        status = session[gt.GT_STATUS_SESSION_KEY]
        if status:
            result = gt.success_validate(challenge, validate, seccode)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            if User.query.filter_by(email=form.email.data).first():
                user=User.query.filter_by(email=form.email.data).first()
                token = user.generate_repassword_token()
                send_email(user.email, u'重置您的密码',
                           'auth/email/repassword', user=user, token=token)
                flash(u'邮件已经发送到您的邮箱：'+user.email+u'请登录查看邮件，并点击链接确认重置！重置后的密码为：123','success')

            return redirect(url_for('main.index'))
    if form.errors:
        flash(u'重置失败.', 'danger')

    return render_template('auth/repassword.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        flash(u'您的邮件已经被确定了！', 'success')
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash(u'您的邮件确认成功!', 'success')
        current_user.confirmed = True
        db.session.add(current_user)
        db.session.commit()
    else:
        flash(u'认证失败，可能链接已经过时！', 'danger')
    return redirect(url_for('main.index'))

@auth.route('/repassword/<token>')
def confirm_repassword(token):
    if User.repassword(token):
        flash(u'您的密码重置成功!请使用初始密码：123登录并修改密码', 'success')
    else:
        flash(u'重置失败，可能链接已经过时！', 'danger')
    return redirect(url_for('main.index'))

#重发邮件
@auth.route('/confirm', methods=['POST'])
@login_required
def resend_confirmation():
    if current_user.is_authenticated and not current_user.confirmed:
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.form[gt.FN_CHALLENGE]
        validate = request.form[gt.FN_VALIDATE]
        seccode = request.form[gt.FN_SECCODE]
        status = session[gt.GT_STATUS_SESSION_KEY]
        if status:
            result = gt.success_validate(challenge, validate, seccode)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            token = current_user.generate_confirmation_token()
            send_email(current_user.email, u'确认您的账户！',
                       'auth/email/confirm', user=current_user, token=token)
            flash(u'新的邮件已经发送到您的邮箱，请查收！', 'success')
            return redirect(url_for('main.index'))
    flash(u'您未登录或您已经确认过邮件！', 'danger')
    return redirect(url_for('main.index'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'您已退出登陆。', 'success')
    return redirect(url_for('main.index'))
