from Database import DatabaseClass
import matplotlib.pyplot as plt
import numpy as np

import pandas as pd
import calendar

# Create an array of month names
months = [calendar.month_name[i] for i in range(1, 13)]

def getTableName(bus):
    return 'ae%s' % f'{bus:02d}'

class Ruler:
    def __init__(self):
        self.rates = None

        self.db = DatabaseClass()

        self.fields = ['Time','2B_Battery_Energy_kWh','2E_Total_Current_A','2K_Total_Mileage_mile','2F_Total_Voltage_percent']
        self.cmd = 'SELECT %s FROM %s'
        # self.cmd = 'SELECT %s FROM %s LIMIT 00,100000'

    def connect(self):
        self.db.connect()

    def fetchData(self,busIndex):
        table = getTableName(busIndex)
        data = self.db.fetch(self.cmd % (','.join(self.fields),table))
        return pd.DataFrame(data,columns=['time','kwh','current','mileage','voltage'])
        # return pd.DataFrame(data,columns=self.fields)

    def close(self):
        self.db.close()
    
    def getAvgConsumptionRate(self,busIndex):
        print('Analyzing for bus %s'%busIndex)

        df = self.fetchData(busIndex)
        
        # calculate mileage difference per row
        df['mileage_difference'] = df['mileage'] - df['mileage'].shift()

        # filter out entries where total mileage is not increasing
        df = df[df['mileage_difference'] > 0]

        # calculate kwh/mile
        # current * voltage / mileage_difference * constant
        RATE_CONSTANT = 10 / 60 / 1000
        df['kwh_per_mile'] = abs(df['current']) * df['voltage'] / df['mileage_difference'] * RATE_CONSTANT

        # segment by month and get average
        df.set_index('time', inplace=True)

        print(df.head(20))
        df = df.resample('M').mean()
        print(df)

        # filter out NaN
        # averages = list(filter(lambda val: not np.isnan(val), df['kwh_per_mile']))
        averages = list(df['kwh_per_mile'])
        
        # make length = 12
        averages += [None for _ in range(12-len(averages))]
        
        return averages
    
    def plot(self,averages):
        fig, axes = plt.subplots(nrows=5, ncols=4,figsize=(8,8))

        i = 0
        for row in range(5):
            for col in range(4):
                plot = axes[row,col]

                averages_for_bus = list(filter(lambda val: val and not np.isnan(val), averages[i,]))
                # print(averages_for_bus)

                plot.hist(averages_for_bus)

                plot.set_xlabel('Average kWh/mile')
                plot.set_ylabel('Density')
                plot.set_title(getTableName(i))
                i += 1

        # Add a title to the figure
        fig.suptitle('Histograms Average kWh/mile by bus')

        # increase spacing
        plt.subplots_adjust(hspace=1,wspace=1)

        # Show the figure
        plt.savefig('plot.jpg')
        plt.show()


if __name__=='__main__':
    ruler = Ruler()
    ruler.connect()

    ruler.getAvgConsumptionRate(1)
    
    # averages = np.array([ruler.getAvgConsumptionRate(bus) for bus in range(1,21)])
    # print(averages)

    ruler.close()

    # averages = np.random.rand(20, 12)

    # ruler.plot(averages)