from Model import Model
import time
def dunc():
    conn, cursor = Model.get_cursor()
    for i in range(301, 306):
        sql = '''
               INSERT
               INTO room(room_id,type_id)
               VALUE({},{})
            '''.format(i, 3)
        cursor.execute(sql)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    t1 = time.localtime(time.time())
    t2 = time.localtime(time.time()*2)
    print(t2.tm_yday)