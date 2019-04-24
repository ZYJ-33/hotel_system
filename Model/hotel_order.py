from Model import Model
from functions import get_time
import time


class hotel_order(Model):
    def __init__(self, **kargs):
        self.uid = kargs.get("uid", None)
        self.room_id = kargs.get("room_id", None)
        self.enter_time = kargs.get("enter_time", None)
        self.leave_time = kargs.get("leave_time", None)
        self.create_time = get_time()
        self.price = kargs.get("total_price", None)
        self.check_start()
        self.save()

    def check_start(self):
        ymd = self.create_time.split(" ")[0]
        enter = time.strptime(self.enter_time, '%Y-%m-%d')
        now = time.strptime(ymd, '%Y-%m-%d')
        if now == enter:
            self.order_status = 'started'
            #hotel_order.update_on_room(self.room_id, self.enter_time, self.leave_time)

    @classmethod
    def update_on_room(cls, room_id, start_date, leave_date):
        conn, cursor = Model.get_cursor()
        sql = '''
            UPDATE room
            SET room_status = 'using',start_date = %s, leave_date = %s
            WHERE room_id = %s
        '''
        cursor.execute(sql, [start_date, leave_date, room_id])
        conn.commit()
        conn.close()

    @classmethod
    def get_all_order(cls):
        conn,cursor = Model.get_cursor()
        sql = '''
            SELECT o.oid,u.name,u.username,o.room_id,o.enter_time,o.leave_time,o.create_time,o.order_status
            FROM hotel_order o ,user u 
            WHERE o.uid = u.uid
        '''
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.commit()
        conn.close()
        return rows

    @classmethod
    def get_order_by_uid(cls, uid):
        conn, cursor = Model.get_cursor()
        sql = '''
                 SELECT o.oid,o.room_id,o.enter_time,o.leave_time,o.create_time,o.order_status
                 FROM hotel_order o 
                 WHERE o.uid = %s AND o.order_status <> 'abort'
              '''
        cursor.execute(sql, [uid])
        rows = cursor.fetchall()
        conn.commit()
        conn.close()
        return rows

    @classmethod
    def get_order_by_oid(cls, oid):
        conn, cursor = Model.get_cursor()
        sql =  '''
                    SELECT t.type, ro.type_id,ro.room_id, ro.enter_time, ro.leave_time, ro.order_status
                    FROM room_type t,(
									SELECT r.type_id,o.room_id, o.enter_time, o.leave_time, o.order_status
									FROM room r, (
																SELECT *
																FROM hotel_order o 
																WHERE o.oid = %s
																)o
									WHERE o.room_id = r.room_id
									)ro
                    WHERE t.type_id = ro.type_id
              '''
        cursor.execute(sql, [oid])
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return result[0]


    @classmethod
    def set_order_abort(cls, uid, oid):
        conn, cursor = Model.get_cursor()
        sql = '''
                    UPDATE hotel_order 
                    SET order_status = 'abort'
                    WHERE uid = %s AND oid = %s
                '''
        cursor.execute(sql, [uid, oid])
        conn.commit()
        print(oid)
        sql = '''
                  SELECT count(*) as c
                  FROM hotel_order o1,(
									   SELECT room_id
									   FROM hotel_order o2
									   WHERE o2.oid = %s
								    ) r1
                  WHERE o1.room_id = r1.room_id AND (o1.order_status='pending' or o1.order_status='started');
        '''
        cursor.execute(sql, [oid])
        result = cursor.fetchall()
        c = result[0]['c']
        if c == 0:
            sql = '''
                SELECT room_id
				FROM hotel_order o2
				WHERE o2.oid = %s
            '''
            cursor.execute(sql, [oid])
            row = cursor.fetchall()
            sql = '''
                UPDATE room
                SET room_status = 'available'
                WHERE room_id = %s
            '''
            cursor.execute(sql, [row[0]['room_id']])
        conn.commit()
        conn.close()


if __name__ == "__main__":
    print(hotel_order.get_order_by_oid(2))