# workflow (terminal):
# cd 'C:\Program Files\Google\Chrome\Application’
# `chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\selenum\ChromeProfile"`
# https://www.hams-online.com/login
# python3 .\driver.py

from selenium import webdriver
from selenium.webdriver.common.by import By

# scrolling
from selenium.webdriver.common.action_chains import ActionChains
import time

# PATH = 'C:\Browser Drivers\chromedriver.exe'

class Driver():
    def __init__(self):
        self.URL = 'https://www.hams-online.com/report/logged-data'

    def connect(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.driver = webdriver.Chrome(options=options)

        self.driver.get(self.URL)

    def fe(self,path):
        return self.driver.find_element(By.XPATH,path)

    def getMonths(self):
        months = self.fe('/html/body/app-root/app-main/section/app-content/app-logged-data/div[1]/div/select[1]')
        # skip 0th ('Month')
        months = months.find_elements(By.TAG_NAME,'option')[1:]
        months = list(map(lambda el:el.get_attribute('innerText'),months))
        return months

    def selectMonth(self,index):
        months = self.fe('/html/body/app-root/app-main/section/app-content/app-logged-data/div[1]/div/select[1]')
        # skip 0th ('Month')
        months = months.find_elements(By.TAG_NAME,'option')[1:]
        months[index].click()

    def getYears(self):
        years = self.fe('/html/body/app-root/app-main/section/app-content/app-logged-data/div[1]/div/select[2]')
        # skip 0th ('Years') and 1st (2017)
        years = years.find_elements(By.TAG_NAME,'option')[2:]
        years = list(map(lambda el:el.get_attribute('innerText'),years))
        return years

    def selectYear(self,index):
        years = self.fe('/html/body/app-root/app-main/section/app-content/app-logged-data/div[1]/div/select[2]')
        # skip 0th ('Years') and 1st (2017)
        years = years.find_elements(By.TAG_NAME,'option')[2:]
        years[index].click()
    
    def scrollToBottom(self,className):
        max_height = self.driver.execute_script("return document.getElementsByClassName('%s')[0].scrollHeight" % className)
        self.driver.execute_script("document.getElementsByClassName('%s')[0].scrollTo(0,%s)" % (className,max_height))

    def selectAllVehicles(self):
        
        btn = []
        while not len(btn):
            btn = self.driver.find_elements(By.XPATH,'/html/body/app-root/app-main/section/app-content/app-logged-data/div[1]/div/div/button')

        btn[0].click()

        vehicles = self.fe('//*[@id="collapseExample"]/ul').find_elements(By.TAG_NAME,'li')
        
        actions = ActionChains(self.driver)
        
        for i in range(len(vehicles)):
        # for i in range(0,2):
            if i < len(vehicles)-2:
                actions.move_to_element(vehicles[i+1]).perform()
            else: # scroll to max height
                self.scrollToBottom('col-3 overflow-auto')
            checkbox = vehicles[i].find_element(By.TAG_NAME,'input')
            try:
                checkbox.click()
            except:
                print('error')

    def downloadAllFiles(self):
        downloadBtn = []
        while not len(downloadBtn):
            downloadBtn = self.driver.find_elements(By.XPATH,'//*[@id="mat-tab-content-0-0"]/div/div/button[1]')

        downloadBtn = downloadBtn[0]
        time.sleep(3)

        # for some reason, retrieving the element here prevents browser from crashing
        el = self.fe('//*[@id="mat-tab-content-0-0"]/div/app-io-base-table/ngx-datatable/div/datatable-body')
        self.scrollToBottom('datatable-body')

        downloadBtn.click()
        

if __name__=='__main__':
    driver = Driver()