import time
from Model import Model
import json


def check_regi_para(**kargs):
    list = []
    list.append(kargs.get("name",None))
    list.append(kargs.get("username", None))
    list.append(kargs.get("password", None))
    list.append(kargs.get("telphone", None))
    list.append(kargs.get("email", None))
    list.append(kargs.get("malebox", None))
    list.append(kargs.get("femalebox", None))
    for i in range(5):
        if list[i] is None:
            return False
    if list[5] is not None and list[6] is not None:
        return False
    elif list[5] is None and list[6] is None:
        return False
    return True

def todict(**kargs):
    form = {}
    for k, v in kargs.items():
        form[k] = v
    return form


def get_time():
    nowtime = time.localtime(int(time.time()))
    return time.strftime("%Y-%m-%d %H:%M:%S", nowtime)


def roomtuple_tolist(roomtuple):
    list = []
    for row in roomtuple:
        for room in row:
            list.append(room)
    return list


def order_pending_to_started():
    conn, cursor = Model.get_cursor()
    get_pending_sql = '''
        SELECT o.room_id, o.enter_time, o.leave_time, o.oid
        FROM hotel_order o 
        WHERE o.order_status = 'pending' AND o.enter_time = current_date()
    '''
    cursor.execute(get_pending_sql)
    rows = cursor.fetchall()
    for row in rows:
        update_using_sql = '''
            UPDATE room r
            SET r.start_date = %s, r.leave_date = %s, r.room_status = 'using'
            WHERE r.room_id = %s
        '''
        cursor.execute(update_using_sql, [row["enter_time"], row["leave_time"], row["room_id"]])

        update_pend_sql = '''
            UPDATE hotel_order o
            SET o.order_status = 'started'
            WHERE o.oid = %s
        '''
        cursor.execute(update_pend_sql, [row['oid']])
    conn.commit()
    conn.close()


def room_using_to_other():
    conn, cursor = Model.get_cursor()
    get_using_sql = '''
            SELECT r.room_id, r.start_date, r.leave_date
            FROM room r
            WHERE r.room_status = 'using' AND leave_date < current_date ()
        '''
    cursor.execute(get_using_sql)
    rows = cursor.fetchall()
    for row in rows:
        order_update_sql = '''
            UPDATE hotel_order o
            SET o.order_status = 'finish'
            WHERE o.room_id = %s AND o.enter_time = %s AND o.leave_time = %s AND o.order_status = 'started'
        '''
        cursor.execute(order_update_sql, [row['room_id'], row['start_date'], row['leave_date']])

        sql = '''
            SELECT count(*) as count
            FROM hotel_order o
            WHERE o.room_id = %s AND o.order_status = 'pending'
        '''
        cursor.execute(sql, [row["room_id"]])
        result = cursor.fetchall()

        if result[0]['count'] > 0:
            update_sql = '''
                UPDATE room r
                SET r.room_status = 'booked', r.start_date = NULL , r.leave_date = NULL
                WHERE r.room_id = %s
            '''
        else:
            update_sql = '''
                UPDATE room r
                SET r.room_status = 'available', r.start_date = NULL , r.leave_date = NULL
                WHERE r.room_id = %s
                '''
        cursor.execute(update_sql, [row["room_id"]])
    conn.commit()
    conn.close()


def jsonlify(data):
    return json.dumps(data)


def hotel_sys_thread():
    while True:
        time.sleep(10)
        order_pending_to_started()
        room_using_to_other()

if __name__ == "__main__":
    room_using_to_other()