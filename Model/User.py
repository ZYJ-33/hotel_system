from Model import Model
import hashlib
from functools import wraps

def sha256_with_salt(str,salt):
    def sha256_hash(s):
        return hashlib.sha256(s.encode("ascii")).hexdigest()
    s = sha256_hash(str)
    s = sha256_hash(s+salt)
    return s


class User(Model):
    salt = "ncasd"
    def __init__(self, **kargs):
        self.name = kargs.get("name", None)
        self.telphone = kargs.get("telphone", None)
        self.username = kargs.get("username", None)
        self.password = kargs.get("password", None)
        self.email = kargs.get("email", None)
        male = kargs.get("femalebox", None)
        if male is None:
            self.sex = "male"
        else:
            self.sex = "female"

    @classmethod
    def checklogin(cls, **kargs):                #后面可以用视图代替基本表查询
        username = kargs.get("username", None)
        password = kargs.get("password", None)
        password = sha256_with_salt(password, User.salt)
        result = User.select_by_username(username)
        if len(result) == 0:
            return False
        user = result[0]
        if user.get("password") == password:
            return True
        return False

    @classmethod
    def hash_pass_checklogin(cls, **kargs):
        username = kargs.get("username", None)
        password = kargs.get("password", None)
        result = User.select_by_username(username)
        if len(result) == 0:
            return False
        user = result[0]
        if user.get("password") == password:
            return True
        return False


    @classmethod
    def get_user_by_username(cls, username):
        conn,cursor = Model.get_cursor()
        sql = '''
            SELECT *
            FROM user 
            WHERE username=%s
        '''
        cursor.execute(sql,[username])
        conn.commit()
        result = cursor.fetchall()
        conn.close()
        return result[0]

    @classmethod
    def select_by_username(cls, username):
        conn, cursor = cls.get_cursor()
        sql = '''
                    SELECT *
                    FROM user 
                    WHERE username = %s
                '''
        cursor.execute(sql, [username])
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return result


    def register(self):
        for k,v in self.__dict__.items():
            if v is None:
                if k is "malebox" or "femalebox":
                    pass
                else:
                    raise Exception

        self.hash_pass()
        self.save()

    def hash_pass(self):
        print(self.password)
        self.password = sha256_with_salt(self.password, User.salt)


    @classmethod
    def get_all_user(cls):     #可用存储过程替代
        conn, cursor = cls.get_cursor()
        sql = '''
            SELECT *
            FROM user u
            WHERE u.level <> 2
        '''
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return result

    @classmethod
    def del_user_by_id(cls, uid):
        conn, cursor = Model.get_cursor()
        sql = '''
            DELETE FROM user
            WHERE uid = %s
        '''
        cursor.execute(sql, [uid])
        conn.commit()
        conn.close()

    @staticmethod
    def is_admin(**kargs):
        if kargs.get("level") == 2:
            return True
        else:
            return False


if __name__ == "__main__":
    username='zyj'

