# python3 -m pip install mysql mysql-connector-python

import mysql.connector
from mysql.connector import Error

import os

HOST = 'localhost'
USER = 'root'
PASSWORD = os.environ.get('MYSQL_SERVER')
DB = 'hams'

class Database():
    def __init__(self):
        self.HOST = HOST
        self.USER = USER
        self.PASSWORD = PASSWORD
        self.DB = DB
    
    # connect to the database
    def connect(self):
        try:
            self.db = mysql.connector.connect(
                host=self.HOST,
                user=self.USER,
                passwd=self.PASSWORD,
                database=self.DB
            )
            self.cur = self.db.cursor(buffered=True)
        except Error as e:
            print("Error while connecting to MySQL:", e)
        else:
            print("Connected to database")
    
    def exec(self,cmd):
        try:
            self.cur.execute(cmd)
        except Error as e:
            print('Command failed:',e)
            return None
        else:
            pass
            # print('Command successfully executed')
    
    def fetch(self,cmd):
        try:
            self.cur.execute(cmd)
            return self.cur.fetchall()
        except Error as e:
            print('Command failed:',e)
            return None

    def createTable(self,table,columns):
        columns = list(map(lambda x: ' '.join(x),columns))
        cmd = 'CREATE TABLE IF NOT EXISTS %s (%s)' % (table,','.join(columns))
        self.exec(cmd)

    def getTableColumns(self,table):
        cmd = 'SELECT * FROM %s' % (table)
        self.cur.execute(cmd)
        return self.cur.column_names

    def commit(self):
        # print('committed')
        self.db.commit()

    def close(self):
        try:
            self.cur.close()
            self.db.close()
        finally:
            print('connection closed')