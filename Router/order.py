from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
)
from datetime import datetime
from functions import get_time
blueprint = Blueprint("order", __name__)
from Model.User import User
from Model.Room import room
from Model.hotel_order import hotel_order
from functions import jsonlify

def check_book_data(jsondata, session):
    if session.get("pending_switch", None)is not None:
        return check_session_data(session, jsondata)
    else:
        return check_data(jsondata)


def check_session_data(data, jsondata):
    enter_time = data.get("enter_time", None)
    leave_time = data.get("leave_time", None)
    room_type = jsondata.get("room_type", None)
    if None or "" in (enter_time, leave_time, room_type):
        return False
    enter = datetime.strptime(enter_time, "%Y-%m-%d")
    leave = datetime.strptime(leave_time, "%Y-%m-%d")
    nowtime = get_time()
    nowtime = nowtime.split(" ")[0]
    now = datetime.strptime(nowtime, "%Y-%m-%d")
    if (leave - enter).days <= 0 or (enter - now).days < 0 or not room_type in ('A', 'B', 'C'):
        return False
    return True


def check_data(data):
    enter_time = data.get("enter_time", None)
    leave_time = data.get("leave_time", None)
    room_type = data.get("room_type", None)
    if None or "" in (enter_time, leave_time, room_type):
        return False
    print(enter_time, leave_time, room_type)
    enter = datetime.strptime(enter_time, "%Y-%m-%d")
    leave = datetime.strptime(leave_time, "%Y-%m-%d")
    nowtime = get_time()
    nowtime = nowtime.split(" ")[0]
    now = datetime.strptime(nowtime, "%Y-%m-%d")
    if (leave - enter).days <= 0 or (enter - now).days < 0 or not room_type in ('A', 'B', 'C'):
        return False
    return True

def outward(rows):
    for row in rows:
        if row["type"] == 'A':
            row["type"] = 'Executive Suite'
        elif row["type"] == 'B':
            row["type"] = 'Twin Room'
        elif row["type"] == 'C':
            row["type"] = 'Single Room'
    return rows

def inward(type):
    if type == "Executive":
        return 'A'
    elif type == "Twin":
        return 'B'
    elif type == "Single":
        return 'C'
    raise Exception


@blueprint.route("/roomtype", methods=["GET", "POST"])
def select_roomtype():
    if session.get("username", None) is None:
        return redirect(url_for("index.index"))
    if request.method == "GET":
        rows = room.get_all_roomtype()
        rows = outward(rows)
        return render_template("select_roomtype.html", rows=rows)
    elif request.method == "POST":
        jsondata = request.json
        type = jsondata["room_type"]
        jsondata["room_type"] = inward(type)
        if check_book_data(jsondata, session):
            if session.get("pending_switch", None) is not None:
                session["room_type"] = jsondata["room_type"]
            else:
                session["enter_time"] = jsondata["enter_time"]
                session["leave_time"] = jsondata["leave_time"]
                session["room_type"] = jsondata["room_type"]
            return jsonlify(url_for("order.select_room"))         #todo:返回可选房间页面
        else:
            order_complete(session)
            return jsonlify(url_for("order.select_room"))                 #todo:返回错误信息


def check_for_selectroom(session):
    if not User.hash_pass_checklogin(**session):
        return False
    a = session.get("enter_time", None)
    b = session.get("leave_time", None)
    c = session.get("room_type", None)
    if None in (a, b, c):
        return False
    return True


@blueprint.route("/room", methods=["GET"])
def select_room():
    if check_for_selectroom(session):
        bookable_rooms = room.get_bookable_room(session["room_type"], session["enter_time"], session["leave_time"])
        print("in select room", session["enter_time"], session["leave_time"])
        return render_template("select_room.html", bookable_rooms=bookable_rooms)
    else:
        return redirect(url_for("index.index"))


def order_complete(session):
    session.pop("room_type")
    session.pop("enter_time")
    session.pop("leave_time")
    session.pop("room_id")
    session.pop("room_price")
    session.pop("total_price")
    if session.get("pending_switch",None) is not None:
        session.pop("pending_switch")


@blueprint.route("/form_order/<int:room_id>", methods=["GET", "POST"])
def form_order(room_id):
    if room_id is None or not check_for_selectroom(session):
        return redirect(url_for("index.index"))
    if request.method == "GET":
        session["room_id"] = room_id
        settle_price(session)
        return render_template("confirm.html", session=session)

    elif request.method == "POST":
        confirm_but = request.form.get("confirm_but", None)
        cancel_but = request.form.get("cancel_but", None)
        if confirm_but is not None:
            print("oid", session.get("oid", None))
            if session.get("oid", None) is not None:                   #换房的逻辑 将原有订单abort 然后生成新单
                hotel_order.set_order_abort(session["uid"], session["oid"])
                session.pop("oid")
            order = hotel_order(**session)
            order_complete(session)
            return redirect(url_for("index.index"))
        elif cancel_but is not None:
            order_complete(session)
            return redirect(url_for("order.select_roomtype"))

def settle_price(session):
    enter_time = session.get("enter_time")
    leave_time = session.get("leave_time")
    room_type = session.get("room_type")
    enter = datetime.strptime(enter_time, "%Y-%m-%d")
    leave = datetime.strptime(leave_time, "%Y-%m-%d")
    day = (leave-enter).days+1
    room_price = room.get_price_by_type(room_type)
    session["room_price"] = room_price
    total_price = room_price*day
    session["total_price"] = total_price

