import cx_Oracle
from django.db import models

# Create your models here.
from main.models import Model_oracleDB_teamd
class oracle_teamd(Model_oracleDB_teamd):
    #food 테이블 연결
    def up_photo_DB(self, normal_id, foodnum, category, mass, candidate_predictions, top_4_probabilities):
        conn = self.myconn()
        cursor = conn.cursor()
        print("category : ", category)
        # 시퀀스 값을 먼저 가져옵니다.
        cursor.execute("SELECT upphoto_seq.nextval FROM dual")
        upphotoid = cursor.fetchone()[0]

        # 가져온 시퀀스 값을 INSERT 문에 사용합니다.
        sql = """
            INSERT INTO upphoto (upphotoid, nnum, foodnum, category, uploaddate, mass, 
            candidate1, candidate2, candidate3, predictrate, candidate1rate, candidate2rate, candidate3rate)
            SELECT :upphotoid, normal_mem.nnum, :foodnum, :category, sysdate, :mass, 
            :candidate1, :candidate2, :candidate3, :predictrate, :candidate1rate, :candidate2rate, :candidate3rate
            FROM normal_mem
            WHERE normal_mem.normal_id = :normal_id
            """
        cursor.execute(sql, upphotoid=upphotoid, normal_id=normal_id, foodnum=foodnum, category=category, mass=mass,
                       candidate1=candidate_predictions[2], candidate2=candidate_predictions[1],
                       candidate3=candidate_predictions[0],
                       predictrate=top_4_probabilities[3], candidate1rate=top_4_probabilities[2],
                       candidate2rate=top_4_probabilities[1], candidate3rate=top_4_probabilities[0])

        cursor.close()
        conn.commit()
        conn.close()

        return str(int(upphotoid))
