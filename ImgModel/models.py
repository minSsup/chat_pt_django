import cx_Oracle
from django.db import models

# Create your models here.
from main.models import Model_oracleDB_teamd
class oracle_teamd(Model_oracleDB_teamd):
    #food 테이블 연결
    def up_photo_DB(self, nnum, foodnum, category, mass):
        conn = self.myconn()
        cursor = conn.cursor()
        # INSERT 문 작성
        sql = """
            INSERT INTO upphoto (upphotoid, nnum, foodnum, category, uploaddate, mass)
            VALUES (upphoto_seq.nextval, :nnum, :foodnum, :category, sysdate, :mass)
            RETURNING upphotoid INTO :upphotoid
            """
        # 반환값을 받을 변수
        upphotoid = cursor.var(cx_Oracle.NUMBER)
        print("*"*50)
        print(upphotoid)
        print("*" * 50)
        # SQL 실행
        cursor.execute(sql, nnum=nnum, foodnum=foodnum, category=category, mass=mass, upphotoid=upphotoid)

        # 시퀀스 번호 가져오기
        file_name = upphotoid.getvalue()[0]

        cursor.close()
        conn.commit()
        conn.close()

        return str(int(file_name))
