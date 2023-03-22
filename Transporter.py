# ========= [ Helper Functions ] =========

import os

import pandas as pd

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

import json
def getDate():
    with open("date.json", "r") as file:
        return json.load(file)

def iterateDate():
    with open("date.json", "r+") as file:
        data = json.load(file)

        data["month"] += 1
        if data["month"] == 12:
            data["month"] = 0
            data["year"] += 1

        # move the file cursor back to the beginning of the file
        file.seek(0)

        # write the updated JSON data to the file
        json.dump(data, file, indent=4)

        # truncate the remaining file contents
        file.truncate()

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

        self.replace = False

    def transport(self):
        
        # get date to transport
        date = getDate()
        year = int(date['year'])
        month = int(date['month'])

        if not (year or month):
            self.replace = True
        
        print(self.replace)

        # fabricate HAMS web portal
        self.driver.connect()
        self.driver.selectAllVehicles()
        time.sleep(5)
        self.driver.selectYear(year)
        self.driver.selectMonth(month)

        # transfer data
        log(1,'Transporting for %s/%s' % (2022+year,1+month))
        self.transportForMonth()
        
        # update date
        iterateDate()
        log(1,'Complete')
    
    def transportForMonth(self):
        paths = self.download()
        self.process(paths)

        self.db.connect()
        self.upload()
        self.db.close()

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
            
            rep = self.replace

            for path in self.org_paths[bus]:
                table = getTableName(bus)
                df = pd.read_csv(path)
                self.db.pushDF(table,df,rep)
                
                # only replace for the VERY FIRST PUSH
                rep = False
    
    def flush(self):
        erasePaths(map(lambda path:os.path.join('.\\data', path),os.listdir('.\\data')))

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