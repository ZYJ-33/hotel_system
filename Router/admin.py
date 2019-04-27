from flask import (
    Blueprint,
    url_for,
    redirect,
    session,
    render_template,
    request,
)
from Router.User import check_login
from functions import jsonlify
from Model.User import User
from Model.hotel_order import hotel_order
from Model.comments import comments
from uuid import uuid4
from functools import wraps

blueprint = Blueprint("admin", __name__)
onpage_dict = {}


def check_admin(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        if User.is_admin(**session):
            return fn(*args, **kwargs)
        else:
            return redirect(url_for("index.index"))
    return decorator


@blueprint.route('/', methods=["GET"])
@check_admin
@check_login
def index():
        return render_template("admin_index.html")


@blueprint.route('/allUser', methods=["GET"])
@check_admin
@check_login
def get_all_users():
    uuid = uuid4()
    uuid = uuid.__str__()
    onpage_dict[uuid] = session["uid"]
    result = User.get_all_user()
    return render_template("admin_alluser.html", users=result, uuid=uuid)


@blueprint.route('/allOrder', methods=["GET"])
@check_admin
@check_login
def get_all_order():
    result = hotel_order.get_all_order()
    return render_template("admin_allorder.html", orders=result)


@blueprint.route('/remove_user/<int:uid>')
@check_admin
@check_login
def remove_user(uid):
    uuid = request.args.get("token", None)
    result_uid = onpage_dict.pop(uuid)
    if session.get("uid") == result_uid:
        User.del_user_by_id(uid)
        return redirect(url_for("admin.get_all_users"))
    else:
        return redirect(url_for("index.index"))



@blueprint.route('/comments', methods=["GET"])
@check_admin
@check_login
def get_comments():
    uuid = uuid4()
    uuid = uuid.__str__()
    onpage_dict[uuid] = session["uid"]
    return render_template("admin_comments.html",uuid = uuid)



@blueprint.route('/comments/del', methods=["POST"])
@check_admin
@check_login
def del_comments():
    json = request.json
    uuid = json.get("token", None)
    result_uid = onpage_dict.pop(uuid)
    if json.get("oid", None) is not None and session["uid"] == result_uid:
        comments.del_comment_by_oid(json.get("oid"))
        return jsonlify(json)
    return

