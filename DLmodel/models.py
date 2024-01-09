from django.db import models
import cx_Oracle as ora
# Create your models here.

from main.models import Model_oracleDB_teamd
class oracle_teamd(Model_oracleDB_teamd):
    #food 테이블 연결
    def food_DB(self):
        conn = self.myconn()
        cursor = conn.cursor()
        sql = "select * from food"
        cursor.execute(sql)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return rows

    def food_Num_DB(self,foodnum):
        conn = self.myconn()
        cursor = conn.cursor()
        sql = "select * from food where foodnum = :foodnum"
        cursor.execute(sql, foodnum=foodnum)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    # memberfood 테이블 연결
    def food_rating_DB(self):
        conn = self.myconn()
        cursor = conn.cursor()
        sql = "select * from memberfood"
        cursor.execute(sql)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return rows

    # member 테이블에 연결
    def normal_member_DB(self, userid):
        conn = self.myconn()
        cursor = conn.cursor()
        sql = "SELECT * FROM NORMAL_MEM WHERE NORMAL_ID = :userid"
        cursor.execute(sql, userid=userid)

        rows = cursor.fetchall()

        # 커서와 연결을 닫습니다.
        cursor.close()
        conn.close()

        return rows

    def member_DB(self,userid):
        conn = self.myconn()
        cursor = conn.cursor()
        sql = "SELECT name,gender,birth FROM members WHERE id = :userid"
        cursor.execute(sql, userid=userid)

        rows = cursor.fetchall()

        # 커서와 연결을 닫습니다.
        cursor.close()
        conn.close()

        return rows

    def diet_DB(self, usernum):
        conn = self.myconn()
        cursor = conn.cursor()
        sql = "SELECT foodnum,mass FROM upphoto WHERE nnum = :usernum and TRUNC(uploaddate) = TRUNC(SYSDATE)"
        cursor.execute(sql, usernum=usernum)

        rows = cursor.fetchall()

        # 커서와 연결을 닫습니다.
        cursor.close()
        conn.close()

        return rows

    def last_food_DB(self,usernum):
        conn = self.myconn()
        cursor = conn.cursor()
        sql = "SELECT foodnum FROM upphoto WHERE uploaddate = (SELECT MAX(uploaddate) FROM upphoto) and nnum = :usernum"
        cursor.execute(sql, usernum=usernum)

        rows = cursor.fetchall()

        # 커서와 연결을 닫습니다.
        cursor.close()
        conn.close()

        return rows