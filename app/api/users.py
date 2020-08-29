from flask import jsonify
from . import api
from flask_login import current_user


@api.route('/userinfo')
def get_user():
    user = current_user
    return jsonify(user.to_json())