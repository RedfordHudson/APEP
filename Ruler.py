import HAMSDatabase
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np

from datetime import datetime
import calendar

# Create an array of month names
months = [calendar.month_name[i] for i in range(1, 13)]

def getTableName(bus):
    return 'ae%s' % f'{bus:02d}'

class Ruler:
    def __init__(self):
        self.rates = None
        
        self.db = HAMSDatabase.HAMSDatabase()

        self.fields = ['time','battery_energy/kWh','current/A','mileage/mile','voltage/V']

        self.total_mileage = []
    
    def connect(self):
        self.db.connect()

    def close(self):
        self.db.close()
    
    def getAverages(self,busIndex):
        print('Analyzing for bus %s'%busIndex)

        if busIndex == 19:
            self.total_mileage.append(0)
            return []

        table = getTableName(busIndex)

        df = self.db.fetchDF(table,self.fields)
        
        df.columns = ['time','battery_energy','current','mileage','voltage']

        # get total mileage
        series = df['mileage']
        total_mileage = series[series.size-1] - series[0]
        self.total_mileage.append(int(total_mileage))

        # df['time'] = df['time'].apply(lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S'))
        df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d %H:%M:%S')

        # calculate mileage difference per row
        df['mileage_difference'] = df['mileage'] - df['mileage'].shift()

        # filter out entries where total mileage is not increasing
        df = df[df['mileage_difference'] > 0]

        if not df.shape[0]:
            print('EMPTY')
            return None

        # calculate kwh/mile

        # constant = (W * min) * (1hr/60min) * (1kW/1000W)
        RATE_CONSTANT = 1 / 60 / 1000

        # current * voltage / mileage_difference * constant
        df['kwh_per_mile'] = abs(df['current']) * df['voltage'] / df['mileage_difference'] * RATE_CONSTANT

        # segment by month and get average
        df.set_index('time', inplace=True)

        df = df.resample('D').mean()

        # filter out NaN
        averages = list(filter(lambda val: not np.isnan(val), df['kwh_per_mile']))
        # averages = list(df['kwh_per_mile'])]
        
        return averages
    
    def plot(self,averages):
        max_value = max([max(avg) if len(avg) else 0 for avg in averages])

        fig, axes = plt.subplots(nrows=5, ncols=4,figsize=(8,8))

        i = 0
        for row in range(5):
            for col in range(4):
                plot = axes[row,col]

                plot.hist(averages[i])

                plot.set_xlim([0,max_value])
                plot.set_ylim([0,6])

                plot.set_xlabel('Average kWh/mile')
                plot.set_ylabel('Density')
                plot.set_title('%s, %s miles' % (getTableName(i+1),self.total_mileage[i]))
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

    # averages = ruler.getAverages(19)

    # print(ruler.total_mileage)
    
    averages = [ruler.getAverages(bus) for bus in range(1,21)]
    # print(averages)
    # print(ruler.total_mileage)

    ruler.close()

    # averages = np.random.rand(20, 31)

    # ruler.total_mileage = list(range(20))

    ruler.plot(averages)