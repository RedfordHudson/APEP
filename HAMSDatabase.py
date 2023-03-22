# ========= [ HAMS Database ] =========

from SSMSDatabase import Database

class HAMSDatabase(Database):
    def __init__(self):

        super().__init__()

        self.hams_fields = ['Time', 'Longitude', 'Latitude', '2A/SOC/%', '2B/Battery Energy/kWh', 
                            '2E/Total Current/A', '2F/Total Voltage/%', '2G/Lowest Battery Temp/F', 
                            '2H/Highest Battery Temp/F', '2I/Speed/mph', '2J/Motor RPM/rpm', 
                            '2K/Total Mileage/mile', '2L/Range/mile', '2M/Left Charge Status/bit', 
                            '2N/Right Charge Status/bit', '2Z/Motor Voltage/V']
        
        self.sql_fields = ['time','longitude','latitude','state_of_charge/%','battery_energy/kWh','current/A',
                           'voltage_percent/%','low_battery_temp/F','high_battery_temp/F','speed/mph','motor_rpm/rpm',
                           'mileage/mile','range/mile','left_charge/bit','right_charge/bit','voltage/V']

    def pushDF(self,table,df,replace=False):
        
        df = df[self.hams_fields]

        df.columns = self.sql_fields
        
        super().pushDF(table,df,replace)

import pandas as pd
def getTableName(bus):
    return 'ae%s' % f'{bus:02d}'
    
if __name__=='__main__':
    db = HAMSDatabase()

    db.connect()
    
    # table = getTableName(1)
    df = pd.read_csv('.\AE-01_119_2020-01-01_22.csv')
    db.pushDF('test32',df,replace=True)