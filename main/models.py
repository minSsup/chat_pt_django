from django.db import models
import cx_Oracle as ora
# Create your models here.
# main/models.py
# Connection, 딥러닝 모델

class Model_oracleDB_teamd:
    def myconn(self):
        conn = ora.connect('chatptDB/chatptDB123@116.122.37.100:1521/xe')
        return conn;