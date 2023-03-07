# ========= [ Helper Functions ] =========

import os

def getPaths(directory,extension):
    paths = filter(lambda path:path.find(extension)!=-1,os.listdir(directory))
    paths = map(lambda path:os.path.join(directory, path),paths)
    return list(paths)

def erasePaths(paths):
    for path in paths:
        os.remove(path)

import re
def getBusFromPath(path) -> int:
    exp = r'AE-?([0-9]+)'
    return int(re.search(exp,path).group(1))

    # return path.split('\\')[-1].split('_')[0].replace('-','_')

def getTableName(bus):
    return 'ae%s' % f'{bus:02d}'

def log(tier,str):
    print('=='*2*tier + ( ' [ %s'  % str))

# ========= [ Transporter ] =========

from datetime import date
import time
from zipfile import ZipFile

import Driver
import HAMSDatabase

class Transporter():
    def __init__(self):

        self.driver = Driver.Driver()
        self.db = HAMSDatabase.HAMSDatabase()

        self.downloadDir = 'C:\\Users\\Redford\\Downloads'

        self.org_paths = {}
        for bus in range(1,21):
            self.org_paths[bus] = []
    
    def testCreateTable(self):
        

        self.db.connect()

        time.sleep(5)

        self.createTables()

        self.db.commit()

        self.db.close()
        
    def transport(self):
        self.driver.connect()

        self.driver.selectAllVehicles()

        years = self.driver.getYears()

        self.db.connect()

        time.sleep(5)

        self.createTables()

        current_month = int(date.today().strftime("%m"))

        for year in range(len(years)):
            log(1,'Transporting for Year: %s' % years[year])

            self.driver.selectYear(year)

            months = self.driver.getMonths()

            for month in range(12):                
                # data only exists after 2018 April
                if year == 0 and month <= 2:
                    continue
                # skip 2018 and 2019
                elif year < 2:
                    continue
                # skip future months
                elif year == len(years)-1 and month >= current_month:
                    break

                log(2,'Transporting for Month: %s' % months[month])

                self.driver.selectMonth(month)

                self.transportForMonth()

        self.db.close()
        
        log(1,'Complete')
    
    def createTables(self):
        log(1,'Creating Tables')
        
        for bus in self.org_paths.keys():
            # wipe
            # DELETE FROM test LIMIT 10
            table = getTableName(bus)
            self.db.createTable(table)
        
        self.db.commit()
    
    def transportForMonth(self):
        paths = self.download()
        self.process(paths)
        self.upload()
        self.flush()
    
    def download(self):
        self.driver.downloadAllFiles()

        log(3,'Downloading')

        paths = getPaths(self.downloadDir,'.zip')

        while (True):
            paths = getPaths(self.downloadDir,'.zip')

            if len(paths):
                break

            time.sleep(3)
        
        return paths
    
    def organizePaths(self,paths):
        # flush org_paths
        for bus in self.org_paths.keys():
            self.org_paths[bus] = []

        for path in paths:
            bus = getBusFromPath(path)

            if (bus not in self.org_paths.keys()):
                print('------------>%s' % bus)
                continue

            self.org_paths[bus].append(path)
    
    def process(self,paths):
        log(3,'Processing')

        zip_path = os.path.join(self.downloadDir, paths[0])
        with ZipFile(zip_path, 'r') as zip:
            zip.extractall('.\\data')
        
        os.remove(zip_path)

        paths = getPaths('.\\data','.csv')

        # process paths organized by bus
        self.organizePaths(paths)

    def upload(self):
        log(3,'Uploading')

        for bus in self.org_paths.keys():
            log(4,'Transporting for Bus: %s' % bus)
            for path in self.org_paths[bus]:
                table = getTableName(bus)
                self.db.pushCSVToDatabase(table,path)

            self.db.commit()
    
    def flush(self):
        erasePaths(map(lambda path:os.path.join('.\\data', path),os.listdir('.\\data')))

    def test(self,path,table):

        self.db.connect()
        
        self.db.createTable(table)
        self.db.commit()

        self.db.pushCSVToDatabase(table,path)
        self.db.commit()

        self.db.close()

# workflow (terminal + browser):
# cd 'C:\Program Files\Google\Chrome\Application’
# `chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\selenum\ChromeProfile"`
# https://www.hams-online.com/login
# python3 .\Transporter.py

if __name__=='__main__':

    # parameters:
    # - download folder
    # - SQL database credentials

    transporter = Transporter()
    transporter.transport()

    # debugging
    # path = getPaths('.\\data','.csv')[0]
    # transporter.test(path,getTableName(1))