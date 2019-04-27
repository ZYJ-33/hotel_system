from Model import Model


class comments(Model):
    def __init__(self, form, **kargs):
        self.com = form.get('com')
        self.oid = kargs.pop('oid')
        self.room_type = kargs.pop('room_type')
        self.uid = kargs.pop('uid')
        self.username = kargs.pop('username')

    @classmethod
    def get_comments_by_type(cls, room_type):
        conn, cursor = Model.get_cursor()
        sql = '''
            SELECT username, com, oid
            FROM comments
            WHERE room_type = %s AND flag = 'visiable'
        '''
        cursor.execute(sql, [room_type])
        rows = cursor.fetchall()
        conn.commit()
        conn.close()
        return rows

    @classmethod
    def get_comments_by_uid(cls, uid):
        conn, cursor = Model.get_cursor()
        sql = '''
                    SELECT oid, com, room_type
                    FROM comments
                    WHERE uid = %s
                '''
        cursor.execute(sql, [uid])
        rows = cursor.fetchall()
        for row in rows:
            sql = '''
                SELECT room_id
                FROM hotel_order
                WHERE oid = %s
            '''
            cursor.execute(sql, row["oid"])
            result = cursor.fetchall()
            row["room_id"] = result[0]["room_id"]
        conn.commit()
        conn.close()
        return rows

    @classmethod
    def get_comments_by_oid(cls, oid):
        conn, cursor = Model.get_cursor()
        sql = '''
                 SELECT com, room_type as type
                 FROM comments
                 WHERE oid = %s AND flag = 'visiable'
              '''
        cursor.execute(sql, [oid])
        row = cursor.fetchall()
        if len(row) == 0:
            return row
        sql = '''
                SELECT room_id
                FROM hotel_order
                WHERE oid = %s
        '''
        cursor.execute(sql, [oid])
        result = cursor.fetchall()
        row[0]["room_id"] = result[0]["room_id"]
        return row

    @classmethod
    def del_comment_by_oid(cls, oid):
        conn, cursor = Model.get_cursor()
        sql = '''
                         UPDATE comments
                         SET flag = 'invisiable'
                         WHERE oid = %s
                 '''
        cursor.execute(sql, [oid])
        conn.commit()
        conn.close()
        if cursor.rowcount == 1:
            return True
        else:
            return False


if __name__ == "__main__":
    print(comments.get_comments_by_type("C"))
    print(comments.get_comments_by_uid(3))
    print(comments.get_comments_by_oid(6))