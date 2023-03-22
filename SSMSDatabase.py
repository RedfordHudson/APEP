import os

# import pyodbc
from sqlalchemy import create_engine,text,engine

class Database():
    def __init__(self):
        self.rates = None
        
        self.SERVER = os.environ.get('SSMS_SERVER')
        self.DB ='BEB'
        self.USER ='rfh'
        self.PASSWORD = os.environ.get('SSMS_PASSWORD')

        self.sql_fields = ['Time','2B_Battery_Energy_kWh','2E_Total_Current_A','2K_Total_Mileage_mile','2F_Total_Voltage_percent']
        self.df_fields = ['time','kwh','current','mileage','voltage']

    def connect(self):
        cnxn_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s"
        cnxn_str = cnxn_str % (self.SERVER,self.DB,self.USER,self.PASSWORD)
        cnxn_url = engine.URL.create("mssql+pyodbc", query={"odbc_connect": cnxn_str})
        self.cnxn = create_engine(cnxn_url).connect()
    
    def close(self):
        self.cnxn.close()

    def fetchDF(self,table,fields=[]):
        fields = '*' if not len(fields) else ','.join(['"%s"'%field for field in fields])

        cmd = 'select %s from %s' % (fields,table)

        df = pd.read_sql_query(sql=text(cmd), con=self.cnxn)

        return df
    
    def pushDF(self,table,df,replace=False):
        df.to_sql(name=table, con=self.cnxn, if_exists=('replace' if replace else 'append'), index=False)
        self.cnxn.commit()

import pandas as pd
import numpy as np

if __name__=='__main__':
    
    data = np.random.rand(5, 3)

    columns = ['A', 'B', 'C']

    df = pd.DataFrame(data=data, columns=columns)


    db = Database()
    db.connect()
    # db.pushDF('test',df,replace=True)
    a = db.fetchDF('test',['A','B'])
    print(a)