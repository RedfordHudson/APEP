import pyodbc
import os

SERVER = os.environ.get('SSMS_SERVER')
DB='BEB'
USER='rfh'
PASSWORD = os.environ.get('SSMS_PASSWORD')

class Database():
    def __init__(self):
        self.SERVER = SERVER
        self.USER = USER
        self.PASSWORD = PASSWORD
        self.DB = DB
    
    # connect to the database
    def connect(self):
        try:
            connection_string = '''DRIVER={SQL Server};
                                    SERVER=%s;
                                    DATABASE=%s;
                                    UID=%s;
                                    PWD=%s'''
            connection_string = connection_string % (self.SERVER,self.DB,self.USER,self.PASSWORD)

            self.db = pyodbc.connect(connection_string)
            self.cur = self.db.cursor()
        except Exception as e:
            print("Error while connecting to SSMS",e)
        else:
            print("Connected to database")
    
    def pushDF(self,table,df):
        df.to_sql(name=table, con=self.db, if_exists='append', index=False)
    
    def exec(self,cmd):
        try:
            self.cur.execute(cmd)
        except Exception as e:
            print('Command failed: ',e)
            # print(cmd)
            return None
        else:
            pass
            # print('Command successfully executed')
    
    def fetch(self,cmd):
        try:
            self.cur.execute(cmd)
            return self.cur.fetchall()
        except Exception as e:
            print('Command failed: ',e)
            return None

    def createTable(self,table,columns):
        columns = list(map(lambda x: ' '.join(x),columns))
        cmd = '''IF OBJECT_ID('%s', 'U') IS NULL
                BEGIN
                    CREATE TABLE %s (
                        %s
                    );
                END
            '''
        cmd = cmd % (table,table,','.join(columns))
        # print(cmd)
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