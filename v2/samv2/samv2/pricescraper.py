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

def RunScraper(search_val, max_iterations=4):
    return_items = []
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service)

    driver.get("https://google.com")

    search_element = driver.find_element(By.CLASS_NAME, "gLFyf")

    search_element.send_keys(search_val)
    search_element.send_keys(Keys.ENTER)

    # Wait for the shopping button to be clickable
    shopping_btn_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "LatpMc")))
    shopping_btn_element.click()

    # Wait for the page to fully load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # Get the initial page height
    initial_page_height = driver.execute_script("return document.body.scrollHeight")

    # Loop to scroll down by 50% page height for max_iterations times
    for _ in range(max_iterations):
        parent_element = driver.find_element(By.XPATH, '//*[@id="rso"]')
        items = parent_element.find_elements(By.CLASS_NAME, "sh-dgr__content")

        # print("Number of items found:", len(items))

        # Loop through each item and print a message
        for item in items:
            # Extract item name
            name = item.find_element(By.CLASS_NAME, "tAxDx").text

            # Extract rating
            rating_element = item.find_element(By.CLASS_NAME, "QIrs8")
            rating = rating_element.text

            # Extract price
            price = item.find_element(By.CLASS_NAME, "a8Pemb").text

            # Extract link
            link = item.find_element(By.CLASS_NAME, 'Lq5OHe')
            href = link.get_attribute("href")

            # Extract TQS if available
            try:
                tqs_element = item.find_element(By.CLASS_NAME, "P6GC4b")
                tqs_value = True
            except NoSuchElementException:
                tqs_value = False

            # Extract delivery conditions
            try:
                delivery_element = item.find_element(By.CLASS_NAME, "vEjMR")
                if "FREE DELIVERY" in delivery_element.text.upper():
                    free_delivery = True
                else:
                    free_delivery = False
            except NoSuchElementException:
                free_delivery = False

            if name and price and link:
                if 'stars'.upper() not in rating.upper():
                    rating = "Not listed"

            i = {
                'name': name,
                'rating': rating,
                'price': price,
                'href': href,
                'tqs': tqs_value,
                'free_delivery': free_delivery,
            }

            if name == "" or price == "" or not name or not price:
                pass
            else:
                return_items.append(i)

        # Scroll down by 50% page height
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")

    driver.quit()

    return return_items