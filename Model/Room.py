from Model import Model
import pymysql
import time
from functions import roomtuple_tolist
from config import sqlpass


def deal_with_datetime(row_tuple):
    rows = []
    for r in row_tuple:
        row = []
        row.append(r[0])
        row.append(r[1].strftime("%Y-%m-%d"))
        row.append(r[2].strftime("%Y-%m-%d"))
        rows.append(row)
    return rows


def usingroom_sql(room_type):
    room_type = room_type.lower()
    if room_type == 'a':
        type_id = 1
    elif room_type == 'b':
        type_id = 2
    elif room_type == 'c':
        type_id = 3
    sql = '''
           SELECT r.room_id, r.start_date, r.leave_date
           FROM room r
           WHERE  r.type_id = {} AND r.room_status = 'using' AND r.leave_date <= %s
       '''.format(type_id)
    return sql


class room_been_booked():
    def __init__(self, room_id):
        self.room_id = room_id
        self.enter_dates = []
        self.leave_dates = []

    def find_leavedate_cloest(self, startdate):
        cloest_leave = room_been_booked.find_cloest_date(self.leave_dates, startdate)
        print("cloest_day and startdate", cloest_leave, startdate )
        return cloest_leave

    def check_startdate_cloest(self, leavedate, cloest_leave):  #找到cloest_start后判断和cloest_leave在room_booked中start_list 和 leave list下标是否相同，相同需要ignore
        cloest_start = room_been_booked.find_cloest_date(self.enter_dates, leavedate)
        print("cloest_day and leave", cloest_start, leavedate)
        if leavedate < cloest_start:
            return True
        else:
            return False


    def check_marginal(self,enter_date,leave_date):
        earliest = room_been_booked.find_earliest_day(self.enter_dates)
        lastest = room_been_booked.find_lastest_day(self.leave_dates)
        if leave_date < earliest or enter_date >lastest:
            return True
        return False

    @classmethod
    def find_cloest_date(cls,date_list,date):
        min_date = None
        min = 10000
        for d in date_list:
            t = abs(d.tm_yday - date.tm_yday)
            if t < min:
                min = t
                min_date = d
        return min_date

    @classmethod
    def find_cloest_greater_date(cls, date_list, date):
        diff = 100000
        cloest_greater_date = date
        for d in date_list:
            if d > date:
                if d.tm_yday - date.tm_yday < diff:
                    cloest_greater_date = d
                    diff = d.tm_yday - date.tm_yday
        return cloest_greater_date



    @classmethod
    def find_earliest_day(cls, date_list):
        min_date = date_list[0]
        for d in date_list:
            if d < min_date:
                min_date = d
        return min_date

    @classmethod
    def find_lastest_day(cls, date_list):
        max_date = date_list[0]
        for d in date_list:
            if d > max_date:
                max_date = d
        return max_date

    def __repr__(self):
        string = str(self.room_id) + "   "
        for e in self.enter_dates:
            string += str(e)
        for e in self.leave_dates:
            string += str(e)
        return string

    def __str__(self):
        return self.__repr__()



class room(Model):
    @classmethod
    def get_price_by_type(cls, type):
        conn, cursor = Model.get_cursor()
        type = type.upper()
        sql = '''
            SELECT price
            FROM room_type
            WHERE type = %s
        '''
        cursor.execute(sql, [type])
        row = cursor.fetchall()
        return row[0]["price"]


    @classmethod
    def get_cursor(cls):
        conn = pymysql.connect("localhost", "root", sqlpass, "hotel_sys")
        cursor = conn.cursor()
        return conn, cursor

    @classmethod
    def get_available_room_interface(cls, room_type):
        sql = '''
            SELECT *
            FROM room_available_{}
        '''.format(room_type.lower())
        conn, cursor = room.get_cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return roomtuple_tolist(result)

    @classmethod
    def get_room_booked(cls, room_type):
        sql = '''
                    SELECT *
                    FROM room_booked_{}
                '''.format(room_type.lower())
        conn, cursor = room.get_cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        result = deal_with_datetime(result)
        return result

    @classmethod
    def get_booked_room_interface(cls, room_type, enter_date, leave_date):
        rows = room.get_room_booked(room_type)
        print(rows)
        return room.result_from_bookedroom(enter_date, leave_date, rows)

    @classmethod
    def result_from_bookedroom(cls, enter_date, leave_date, rows):   #
        total_room = []
        room_result = []
        if len(rows) > 0:
            r = room_been_booked(rows[0][0])
            enter_date = time.strptime(enter_date, '%Y-%m-%d')
            leave_date = time.strptime(leave_date, '%Y-%m-%d')

            for row in rows:
                if r.room_id == row[0]:
                    r.enter_dates.append(time.strptime(row[1], '%Y-%m-%d'))
                    r.leave_dates.append(time.strptime(row[2], '%Y-%m-%d'))
                else:
                    total_room.append(r)
                    r = room_been_booked(row[0])
                    r.enter_dates.append(time.strptime(row[1], '%Y-%m-%d'))
                    r.leave_dates.append(time.strptime(row[2], '%Y-%m-%d'))

            total_room.append(r)

            for room_rep in total_room:
                if room_rep.check_marginal(enter_date, leave_date):
                    room_result.append(room_rep.room_id)
                elif room.check_booked(room_rep, enter_date, leave_date):
                    room_result.append(room_rep.room_id)
        return room_result

    @classmethod
    def check_booked(cls, room_rep, enter_date, leave_date):
        cloest_leave = room_rep.find_leavedate_cloest(enter_date)
        if enter_date < cloest_leave:
            return False
        cloest_start = room_rep.find_cloest_greater_date(room_rep.enter_dates, cloest_leave)
        if enter_date > cloest_leave and leave_date <cloest_start:
            return True
        return False

    @classmethod
    def get_using_room_interface(cls, room_type, enter_date, leave_date):
        conn, cursor = room.get_cursor()
        sql = usingroom_sql(room_type)
        cursor.execute(sql, [enter_date])
        conn.commit()
        rows = cursor.fetchall()
        l = []               #r.room_id, r.start_date, r.leave_date
        for row in rows:
            if row[2].strftime("%Y-%m-%d") >= enter_date:
                pass
            else:
                l.append(row)
        rows = tuple(l)
        if len(rows) == 0:
            return []
#        return tuple(ok_list), tuple(booked_list)

        else:
            oks, bookeds = room.get_possible_booked(rows, conn, cursor)
            bookeds = deal_with_datetime(bookeds)
            result = room.result_from_bookedroom(enter_date, leave_date, bookeds)
            for ok in oks:
                result.append(ok[0])
            return result

    @classmethod
    def get_possible_booked(cls, rows, conn, cursor):
        booked_list = []
        ok_list = []
        for row in rows:
            sql = '''
                SELECT o.room_id, o.enter_time, o.leave_time
                FROM hotel_order o
                WHERE  o.order_status = 'pending' AND o.room_id  = %s
            '''
            cursor.execute(sql, [row[0]])
            conn.commit()
            result = cursor.fetchall()
            if len(result) > 0:
                for r in result:
                    booked_list.append(r)
            else:
                ok_list.append(row)
        return tuple(ok_list), tuple(booked_list)


    @classmethod
    def get_bookable_room(cls, room_type, enter_date, leave_date):
        al = room.get_available_room_interface(room_type)
        bl = room.get_booked_room_interface(room_type, enter_date, leave_date)
        ul = room.get_using_room_interface(room_type, enter_date, leave_date)
        print("al ", al)
        print("bl ", bl)
        print("ul ", ul)
        return al+bl+ul


    @classmethod
    def get_room_for_started(cls, room_type, enter_date, leave_date):
        al = room.get_available_room_interface(room_type)
        bl = room.get_booked_room_interface(room_type, enter_date, leave_date)
        return al + bl

    @classmethod
    def get_all_roomtype(cls):
        conn, cursor = Model.get_cursor()
        sql = '''
            SELECT *
            FROM room_type
        '''
        cursor.execute(sql)
        return cursor.fetchall()

    @classmethod
    def started_room_switch(cls, oldroom, newroom, oid, enter_time, leave_time):
        conn, cursor = Model.get_cursor()
        sql = '''
                    UPDATE room
                    SET room_status = 'using',start_date = %s, leave_date =%s
                    WHERE room_id = %s
                '''
        cursor.execute(sql, [enter_time, leave_time, newroom])
        sql = '''
            UPDATE hotel_order
            SET room_id = %s
            WHERE oid = %s
        '''
        cursor.execute(sql, [newroom, oid])
        sql ='''
                SELECT count(*) as c
                FROM hotel_order o1
                WHERE o1.room_id = %s AND o1.order_status='pending'
                '''
        cursor.execute(sql, [oldroom])
        result = cursor.fetchall()
        c = result[0]['c']
        if c == 0:
            sql = '''
                        UPDATE room
                        SET room_status = 'available',start_date = NULL, leave_date = NULL
                        WHERE room_id = %s
                    '''
        else:
            sql = '''
                        UPDATE room
                        SET room_status = 'booked',start_date = NULL, leave_date = NULL
                        WHERE room_id = %s
                    '''
        cursor.execute(sql, [oldroom])
        conn.commit()
        conn.close()









if __name__ == "__main__":
    print(room.get_bookable_room('a',"2019-7-11","2019-7-12"))
    #room.result_from_usingroom('A',"2019-7-11","2019-7-12")
    '''
    #room_been_booked.find_cloest_date()
    t1 = time.strptime("2019-7-11", "%Y-%m-%d")
    t2 = time.strptime("2019-4-12", "%Y-%m-%d")
    t3 = time.strptime("2019-2-5", "%Y-%m-%d")
    t4 = time.strptime("2019-1-18", "%Y-%m-%d")
    t5 = time.strptime("2019-3-16", "%Y-%m-%d")
    t6 = time.strptime("2019-7-28", "%Y-%m-%d")
    t7 = time.strptime("2019-9-8", "%Y-%m-%d")
    t8 = time.strptime("2019-11-28", "%Y-%m-%d")
    t9 = time.strptime("2019-12-3", "%Y-%m-%d")
    t10 = time.strptime("2019-2-1", "%Y-%m-%d")
    list = [t1,t2,t3,t4,t5,t6,t7,t8,t9,t10]
    t = time.strptime("2019-2-12", "%Y-%m-%d")
    print(time.strftime("%Y-%m-%d", room_been_booked.find_cloest_date(list,t)))
    '''