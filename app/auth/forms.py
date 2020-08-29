# coding: utf-8
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email,EqualTo


class LoginForm(Form):
    email = StringField(u'电子邮件', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField(u'密码', validators=[DataRequired()])

class RegisterForm(Form):
    email = StringField(u'电子邮件', validators=[DataRequired(), Length(1, 64),Email()])
    qq= StringField(u'QQ号', validators=[DataRequired(), Length(1, 64)])
    tel = StringField(u'手机号', validators=[DataRequired(), Length(1, 64)])
    wechat = StringField(u'微信号', validators=[DataRequired(), Length(1, 64)])
    comname = StringField(u'公司名', validators=[Length(1, 64)])
    username = StringField(u'昵称', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField(u'密码', validators=[
        DataRequired(), EqualTo('password2', message=u'两次输入密码不一致！')])
    password2 = PasswordField(u'确认密码', validators=[DataRequired()])


class RepasswordForm(Form):
    email = StringField(u'电子邮件', validators=[DataRequired(), Length(1, 64),
                                             Email()])