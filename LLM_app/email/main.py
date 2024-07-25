import sys

from selenium import webdriver


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless') # this is must
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')


driver = webdriver.Chrome(options=chrome_options)

import time
from selenium.webdriver.common.by import By


from bs4 import BeautifulSoup
import time



driver.get("https://www.linkedin.com/login")


time.sleep(4)

username = driver.find_element(by=By.XPATH, value="//input[@name='session_key']")
password = driver.find_element(by=By.XPATH, value="//input[@name='session_password']")
username.send_keys("aditshah06@gmail.com")
password.send_keys("ADIT1112")
time.sleep(4)
submit = driver.find_element(by=By.XPATH, value="//button[@type='submit']").click()
time.sleep(4)

company_names = []
element_list=[]
for page in range(1, 8, 1):

    # page_url = "https://www.linkedin.com/search/results/people/?activelyHiringForJobTitles=%5B%22-100%22%5D&geoUrn=%5B%22104423466%22%2C%2290009553%22%5D&keywords=ea%20sports&origin=FACETED_SEARCH&page="+str(page)+"&sid=ZNt&spellCorrectionEnabled=false"
    page_url="https://www.linkedin.com/search/results/people/?keywords=darkvision&origin=FACETED_SEARCH&page={}&sid=*H)".format(page)
    driver.get(page_url)

    src = driver.page_source
    soup = BeautifulSoup(src, 'lxml')
    company_name_html = soup.find_all(
      'div', {'class': 't-roman t-sans'})
    for name in company_name_html:
        company_names.append(name.text.strip().strip().split("View", 1)[0])
        # print(name.text.strip().split("View", 1)[0])

print(company_names)

def convert_name_format(name):
    name=name.lower()
    return (name.split(" ")[0],name.split(" ")[1])

import numpy as np

converted_names = np.vectorize(convert_name_format)(company_names)


for i in range(len(converted_names[0])):
  print(converted_names[0][i]+"."+converted_names[1][i]+"@darkvision.com")