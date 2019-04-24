from flask import (
    Blueprint,
    request,
    session,
    redirect,
    url_for,
    render_template,
)
from Model.User import User
from Model.hotel_order import hotel_order
from Model.comments import comments
from functions import jsonlify
from Router.order import outward
blueprint = Blueprint('comments', __name__)


# SELECT t.type, ro.type_id,ro.room_id, ro.enter_time, ro.leave_time, ro.order_status
@blueprint.route("/add/<int:oid>", methods=['GET', 'POST'])
def add(oid):
    if User.hash_pass_checklogin(**session):
        if request.method == 'GET':
            row = hotel_order.get_order_by_oid(oid)
            row["oid"] = oid
            session["room_type"] = row["type"]
            row = outward([row])
            return render_template("finish_order_comment.html", order=row[0])
        elif request.method == 'POST':
            com = request.form["com"]
            room_type = session["room_type"]
            uid = session["uid"]
            username = session["username"]
            d = dict(
                com=com,
                room_type=room_type,
                oid=oid,
                uid=uid,
                username=username,
            )
            c = comments(d)
            c.save()
            return redirect(url_for("User.user_orders"))
    else:
        return redirect(url_for("index.index"))


@blueprint.route("/comment of oid/<int:oid>", methods=["GET"])
def find_comment_by_oid(oid):
    result = comments.get_comments_by_oid(oid)
    result = outward(result)
    return render_template("single_order_comment.html", result=result)

def inward(type):
    if type == "Executive":
        return 'A'
    elif type == "Twin":
        return 'B'
    elif type == "Single":
        return 'C'
    raise Exception

@blueprint.route("/room_type comment", methods=["GET", "POST"])
def find_comment_by_roomtype():
    if request.method == "GET":
        return render_template("comment_by_roomtype.html")
    elif request.method == "POST":
        json = request.json
        json["room_type"] = inward(json["room_type"].split(" ", 1)[0])
        room_type = json.get("room_type", None)
        if room_type is None:
            return redirect(url_for("find_comment_by_roomtype"))
        rows = comments.get_comments_by_type(room_type)
        return jsonlify(rows)

