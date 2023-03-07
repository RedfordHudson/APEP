import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By

PATH = 'C:\Browser Drivers\chromedriver.exe'

URL = "https://www.hams-online.com/login"
URL2 = 'https://www.hams-online.com/dashboard/fleet/map'

# IMPORTANT: remove default from end
PROFILE_PATH = 'C:\\Users\\Redford\\AppData\\Local\\Google\\Chrome\\User Data'

def createDriver():
    options = webdriver.ChromeOptions()
    options.add_argument('--user-data-dir={pp}'.format(pp=PROFILE_PATH))
    return uc.Chrome(options=options)

def login(driver):
    driver.get(URL)

    # wait for DOM to load before scraping
    driver.implicitly_wait(20)

    username = driver.find_element(By.XPATH,'//*[@id="email"]')
    password = driver.find_element(By.XPATH,'//*[@id="password"]')

    # username.send_keys(PORTAL_USERNAME)
    # password.send_keys(PORTAL_PASSWORD)

if __name__=='__main__':
    # driver = createDriver()

    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)

    driver.get(URL)

while(True):
    pass