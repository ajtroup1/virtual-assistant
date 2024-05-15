from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
from rest_framework import status
from rest_framework.response import Response

def RunYoutubeScraper(query):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors') 

    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(f"https://www.youtube.com/results?search_query={query}")

    try:
        while True:
            # Attempt to find the element
            element = driver.find_element(By.XPATH, "/html/body")
            time.sleep(2.5)
    except NoSuchElementException:
        # Handle the case where the element is not found
        print('**************')
        driver.quit()
        return Response({"Exiting scraper"}, status=status.HTTP_204_NO_CONTENT)