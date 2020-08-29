# coding: utf-8
from StringIO import StringIO

from flask import send_file,redirect,url_for,flash

from . import username
from flask import render_template,request
from flask_login import login_required
from ..models import User,Article

@username.route('/<int:id>')
def detials(id):
    user=User.query.get_or_404(id)
    if user.confirmed==False:
        flash('用户未确认邮箱！','danger')
        return redirect(url_for('main.index'))
    if user.banded==True:
        flash('用户由于某种原因处于禁止状态！','danger')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.filter_by(author_id=id).order_by(Article.update_time.desc()).paginate(
        page, per_page=3,
        error_out=False)
    articles = pagination.items
    return render_template('username/user_info.html', user=user, articles=articles,
                           pagination=pagination, endpoint='.detials',id=id)

@username.route('/qrcode/<int:id>')
def qrcode(id):
    import qrcode
    img = qrcode.make("http://www.jiakaozuche.com/zhuye/"+str(id))
    #img.save("./test.png")

    return _serve_pil_image(img)


def _serve_pil_image(pil_img):
    img_io = StringIO()
    pil_img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png', cache_timeout=0)