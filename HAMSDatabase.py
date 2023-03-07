# ========= [ Helper Functions ] =========

from math import isnan

def isNULL(val):
    try:
        float(val)
        return isnan(val)
    except:
    # except ValueError:
        return False

def getFields(columns):
    return list(map(lambda column:column[0],columns))

# column names cannot begin with a number
def fixKey(key):
    key = key.replace('/','_').replace(' ','_').replace('%','percent')
    if key.find('2') == 0:
        key = key[1:]
    return key

# ========= [ HAMS Database ] =========

import pandas
from SSMSDatabase import Database

class HAMSDatabase(Database):
    def __init__(self):

        super().__init__()

        self.columns = [('Time', 'datetime'), ('Longitude', 'float'),
            ('Latitude', 'float'), ('2A/SOC/%', 'float'),
            ('2B/Battery Energy/kWh', 'float'), ('2E/Total Current/A', 'float'),
            ('2F/Total Voltage/%', 'float'), ('2G/Lowest Battery Temp/F', 'float'),
            ('2H/Highest Battery Temp/F', 'float'), ('2I/Speed/mph', 'float'),
            ('2J/Motor RPM/rpm', 'float'), ('2K/Total Mileage/mile', 'float'),
            ('2L/Range/mile', 'float'), ('2M/Left Charge Status/bit', 'varchar(45)'),
            ('2N/Right Charge Status/bit', 'varchar(45)'),
            ('2Z/Motor Voltage/V', 'float')]
            # , ('3C/Regen/kWh', 'float')]

        # for converting HAMS format to SQL format
        self.table_params = self.setTableParameters()
        self.modified_table_params = self.setModifiedTableParameters()

    def setTableParameters(self):
        csvFields = getFields(self.columns)
        sqlFields = getFields(self.fixColumns())
        dict = {}
        for field in csvFields:
            dict[field]=fixKey(field)

        return {
            'csvFields':csvFields,
            'sqlFields':sqlFields,
            'dict':dict
        }
    
    def setModifiedTableParameters(self):
        a = ['2F/Total Voltage/%', '2K/Total Mileage/mile', '2L/Range/mile']
        b = ['2F/Total Voltage/V', '2K/Total Mileage/miles', '2L/Range/miles']

        # b -> a

        csvFields = self.table_params['csvFields']

        # print(csvFields)
        for x in range(3):
            for y in range(len(csvFields)):
                if csvFields[y] == b[x]:
                    csvFields[y] = a[x]
        # print(csvFields)

        dict = self.table_params['dict']
        for i in range(3):
            dict[b[i]] = a[i]

        return {
            'csvFields':csvFields,
            'sqlFields':self.table_params['sqlFields'],
            'dict':dict
        }
    
    def fixColumns(self):
        return list(map(lambda column:(fixKey(column[0]),column[1]),self.columns))

    def createTable(self,table):
        super().createTable(table,self.fixColumns())

    def pushCSVToDatabase(self,table,path):
        
        fields = ','.join(self.table_params['sqlFields'])
        cmd = 'insert into %s (%s) values (' % (table, fields)
        cmd += '%s)'
        # print(cmd)

        df = pandas.read_csv(path)
        
        try:
            df = df[self.table_params['csvFields']].rename(self.table_params['dict'])
        except:
            df = df[self.modified_table_params['csvFields']].rename(self.modified_table_params['dict'])

        for index,row in df.iterrows():
            values = ','.join(map(lambda val:'NULL' if isNULL(val) else  "'%s'" % str(val), row))
            super().exec(cmd % values)
            # return
        super().commit()
    
if __name__=='__main__':
    print('running')

    db = HAMSDatabase()
    db.connect()

    # db.createTable('test',db.fixColumns())
    db.createTable('test500',)
    db.commit()

    db.close()