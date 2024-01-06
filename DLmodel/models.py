from django.db import models
import cx_Oracle as ora
# Create your models here.

from main.models import Model_oracleDB_teamd
class oracle_teamd(Model_oracleDB_teamd):
    def origin_DB(self):
        conn = self.myconn()
        cursor = conn.cursor()
        sql = "select * from members"
        rows = cursor.execute(sql)
        rows = cursor.fetchall()

        return rows

