from flask import (
    Blueprint,
    request,
    session,
    render_template,
    redirect,
    url_for,
)
from Model.User import User
from Model.hotel_order import hotel_order
from Model.Room import room
from functions import (
    todict,
    check_regi_para,
)
import pymysql
from Router.order import outward


blueprint = Blueprint("User", __name__)


@blueprint.route("/login", methods=["POST"])
def login():
    if session.get("username", None) is not None:
        return redirect(url_for("index.index"))
    if  request.method == "POST":
        form = request.form
        username = form.get("username", None)
        password = form.get("password", None)
        if username is None or password is None:
            return redirect(url_for("index.index"))
        if User.checklogin(username=username, password=password):
            ud = User.get_user_by_username(username)
            session["uid"] = ud["uid"]
            session["username"] = ud["username"]
            session["password"] = ud["password"]
            session["level"] = ud["level"]
            return redirect(url_for("index.index"))
        else:
            return redirect(url_for("index.index"))


@blueprint.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("index.index"))


@blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("regist.html")
    elif request.method == "POST":
        form = request.form
        form = todict(**form)
        print('in register', form)
    if check_regi_para(**form):
        u = User(**form)
        try:
            u.register()
        except pymysql.err.IntegrityError as e:
            return redirect(url_for("User.register"))
        return redirect(url_for("index.index"))
    else:
        return redirect(url_for("User.register"))



@blueprint.route("/center", methods=["GET"])
def center_index():
    return render_template("user_center.html")


@blueprint.route("/center/orders", methods=["GET"])
def user_orders():
    if User.hash_pass_checklogin(**session):
        rows = hotel_order.get_order_by_uid(session.get("uid"))
        return render_template("user_center_order.html", orders=rows)
    else:
        return redirect(url_for("index.index"))


@blueprint.route("/center/checkout/<int:oid>", methods=["GET"])
def user_checkout_in_adv(oid):
    if User.hash_pass_checklogin(**session):
        uid = session.get("uid")
        hotel_order.check_out_adv(uid, oid)
        return redirect(url_for("User.user_orders"))
    else:
        return redirect(url_for("index.index"))


@blueprint.route("/center/cancel/<int:oid>", methods=["GET"])
def user_cancel_order(oid):
    if User.hash_pass_checklogin(**session):
        uid = session.get("uid")
        print("oid", oid)
        hotel_order.set_order_abort(uid, oid)
        return redirect(url_for("User.user_orders"))
    else:
        return redirect(url_for("index.index"))


@blueprint.route("/center/switch/<int:oid>", methods=["GET"])
def user_switch_room(oid):
    if User.hash_pass_checklogin(**session):
        order = hotel_order.get_order_by_oid(oid)
        order["enter_time"] = order["enter_time"].strftime("%Y-%m-%d")
        order["leave_time"] = order["leave_time"].strftime("%Y-%m-%d")
        if order["order_status"] not in ("pending", "started"):
            return redirect(url_for("User.user_orders"))
        elif order["order_status"] == "pending":
            session["enter_time"] = order["enter_time"]
            session["leave_time"] = order["leave_time"]
            session["pending_switch"] = 'True'
            if session.get("oid", None) is None:
                session["oid"] = oid
            rows = room.get_all_roomtype()
            rows = outward(rows)
            return render_template("pending_order_select_roomtype.html", rows=rows)
        else:
            list = room.get_room_for_started(order["type"], order["enter_time"], order["leave_time"])
            session["old_room_id"] = order["room_id"]
            session["started_oid"] = oid
            session["enter_time"] = order["enter_time"]
            session["leave_time"] = order["leave_time"]
            return render_template("room_for_started.html", list=list)
    else:
        return redirect(url_for("index.index"))


@blueprint.route("/start_room_switch/<int:room_id>", methods=["GET"])
def started_room_switch(room_id):
    if User.hash_pass_checklogin(**session):
        old_room_id = session.pop("old_room_id")
        oid = session.pop("started_oid")
        enter_time = session.pop("enter_time")
        leave_time = session.pop("leave_time")
        room.started_room_switch(old_room_id, room_id, oid, enter_time, leave_time)
        return redirect(url_for("User.user_orders"))
    else:
        return redirect(url_for("index.index"))

