from flask import (
    Blueprint,
    url_for,
    redirect,
    session,
    render_template,
    request,
)
from functions import jsonlify
from Model.User import User
from Model.hotel_order import hotel_order
from Model.comments import comments
blueprint = Blueprint("admin", __name__)


@blueprint.route('/', methods=["GET"])
def index():
    if not User.hash_pass_checklogin(**session):
        return redirect(url_for("index.index"))
    if not User.is_admin(**session):
        return redirect(url_for("index.index"))
    else:
        return render_template("admin_index.html")


@blueprint.route('/allUser', methods=["GET"])
def get_all_users():
    if not User.hash_pass_checklogin(**session):
        return redirect(url_for("index.index"))
    if not User.is_admin(**session):
        return redirect(url_for("index.index"))
    result = User.get_all_user()
    return render_template("admin_alluser.html", users = result)


@blueprint.route('/allOrder', methods=["GET"])
def get_all_order():
    if not User.hash_pass_checklogin(**session):
        return redirect(url_for("index.index"))
    if not User.is_admin(**session):
        return redirect(url_for("index.index"))
    result = hotel_order.get_all_order()
    return render_template("admin_allorder.html", orders=result)


@blueprint.route('/remove_user/<int:uid>')
def remove_user(uid):
    if not User.hash_pass_checklogin(**session):
        return redirect(url_for("index.index"))
    if not User.is_admin(**session):
        return redirect(url_for("index.index"))
    User.del_user_by_id(uid)
    return redirect(url_for("admin.get_all_users"))


@blueprint.route('/comments', methods=["GET"])
def get_comments():
    if not User.hash_pass_checklogin(**session):
        return redirect(url_for("index.index"))
    if not User.is_admin(**session):
        return redirect(url_for("index.index"))
    return render_template("admin_comments.html")


@blueprint.route('/comments/del', methods=["POST"])
def del_comments():
    if not User.hash_pass_checklogin(**session):
        return redirect(url_for("index.index"))
    if not User.is_admin(**session):
        return redirect(url_for("index.index"))
    json = request.json
    if json.get("oid", None) is not None:
        comments.del_comment_by_oid(json.get("oid"))
        return jsonlify(json)
    return

