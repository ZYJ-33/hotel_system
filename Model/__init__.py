import pymysql
from config import sqlpass

class Model(object):
    @classmethod
    def tablename(cls):
        return cls.__name__.lower()

    def save(self):
        conn,cursor = Model.get_cursor()
        sql = self.get_insert_sql()
        para = []
        for v in self.__dict__.values():
            para.append(v)
        print('In save', para)
        cursor.execute(sql, para)
        conn.commit()
        conn.close()


    @classmethod
    def get_cursor(cls):
        conn = pymysql.connect("localhost", "root", sqlpass, "hotel_sys",cursorclass = pymysql.cursors.DictCursor)
        cursor = conn.cursor()
        return conn, cursor


    def get_insert_sql(self):
        i = 0
        tablename = self.tablename()
        sql = '''INSERT 
INTO {}('''.format(tablename)
        value_sql = 'VALUE('
        for k in self.__dict__.keys():
            sql += k
            value_sql += '%s'
            if i == self.__dict__.__len__() - 1:
               break;
            i = i + 1
            sql += ','
            value_sql += ','
        sql +=')'
        value_sql += ')'
        return sql +"\n" +value_sql





if __name__ == "__main__":
    cursor = Model.get_cursor()
    sql = '''
        SELECT *
        FROM room_type
    '''
    cursor.execute(sql)
    d = cursor.fetchall()
    print(d)