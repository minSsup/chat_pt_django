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

    # 나이대 별로 등록된 음식 리스트 20개 뽑기
    def list_age_food_info(self, usernum, ageDecade):
        conn = self.myconn()
        cursor = conn.cursor()

        # 나이대의 상한 값을 계산
        ageDecadeUpper = ageDecade + 9

        sql = """
        SELECT * FROM (
          SELECT N.NICKNAME, F.FOODNUM, F.FOODCAL, F.FOODIMG, F.FOOD_TAN, F.FOOD_DAN, F.FOOD_GI, F.FOODNAME, U.UPLOADDATE,U.CATEGORY
          FROM MEMBERS M
          INNER JOIN NORMAL_MEM N ON M.ID = N.NORMAL_ID
          INNER JOIN UPPHOTO U ON N.NNUM = U.NNUM
          INNER JOIN FOOD F ON U.FOODNUM = F.FOODNUM
          WHERE FLOOR(MONTHS_BETWEEN(SYSDATE, M.BIRTH) / 12) BETWEEN :ageDecade AND :ageDecadeUpper
          AND M.ROLE = 'NORMAL'
          AND N.NNUM != :usernum
          ORDER BY U.UPLOADDATE DESC
        )
        WHERE ROWNUM <= 25
        """

        # 바인딩 변수와 함께 쿼리 실행
        cursor.execute(sql, {'usernum': usernum, 'ageDecade': ageDecade, 'ageDecadeUpper': ageDecadeUpper})

        rows = cursor.fetchall()

        # 커서와 연결을 닫습니다.
        cursor.close()
        conn.close()

        return rows

    def list_purpose_food_info(self, usernum, purpose):
        conn = self.myconn()
        cursor = conn.cursor()

        sql = """
        SELECT * FROM (
          SELECT N.NICKNAME, F.FOODNUM, F.FOODCAL, F.FOODIMG, F.FOOD_TAN, F.FOOD_DAN, F.FOOD_GI, F.FOODNAME, U.UPLOADDATE,U.CATEGORY
          FROM MEMBERS M
          INNER JOIN NORMAL_MEM N ON M.ID = N.NORMAL_ID
          INNER JOIN UPPHOTO U ON N.NNUM = U.NNUM
          INNER JOIN FOOD F ON U.FOODNUM = F.FOODNUM
          WHERE N.PURPOSE = :purpose
          AND M.ROLE = 'NORMAL'
          AND N.NNUM != :usernum
          ORDER BY U.UPLOADDATE DESC
        )
        WHERE ROWNUM <= 25
        """

        # 바인딩 변수와 함께 쿼리 실행
        cursor.execute(sql, {'purpose': purpose,'usernum': usernum })

        rows = cursor.fetchall()

        # 커서와 연결을 닫습니다.
        cursor.close()
        conn.close()

        return rows
