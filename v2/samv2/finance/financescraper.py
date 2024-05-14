from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
from .models import Stock, HistoricalData

def RunFinanceScraper(stock_id):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors') 

    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://finance.yahoo.com/")

    search_bar = driver.find_element(By.XPATH, '//*[@id="ybar-sbq"]')
    search_bar.send_keys(stock_id)
    time.sleep(0.5)
    search_bar.send_keys(Keys.ENTER)

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="nimbus-app"]/section/section/aside/section/nav/ul/li[1]/a')))

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 12);")

    # Collect initial stock info
    name = driver.find_element(By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/section[1]/div[1]/div/section/h1').text
    percent_change = driver.find_element(By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/section[1]/div[2]/div[1]/section/div/section[1]/div[1]/fin-streamer[3]/span').text
    price = driver.find_element(By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/section[1]/div[2]/div[1]/section/div/section[1]/div[1]/fin-streamer[1]/span').text
    fiftytwo_week_range = driver.find_element(By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/div[2]/ul/li[5]/span[2]/fin-streamer').text
    market_cap = driver.find_element(By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/div[2]/ul/li[9]/span[2]/fin-streamer').text
    pe_ratio = driver.find_element(By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/div[2]/ul/li[11]/span[2]/fin-streamer').text
    earnings_date = driver.find_element(By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/div[2]/ul/li[13]/span[2]').text

    print(name)
    print(percent_change)
    print(price)
    print(fiftytwo_week_range)
    print(market_cap)
    print(pe_ratio)
    print(earnings_date)

    driver.execute_script("window.scrollTo(0, 0);")

    # Navigate to profile
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="nimbus-app"]/section/section/aside/section/nav/ul/li[7]'))).click()

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 10);")

    # Get profile info
    try:
        sector = driver.find_element(By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/section[2]/section[2]/div/dl/div[1]/dd/a').text
        industry = driver.find_element(By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/section[2]/section[2]/div/dl/div[2]/a').text
        full_time_employees = driver.find_element(By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/section[2]/section[2]/div/dl/div[3]/dd/strong').text
    except NoSuchElementException:
        full_time_employees = "Not listed"

    description = driver.find_element(By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/section[3]/section[1]/p').text

    print(sector)
    print(industry)
    print(full_time_employees)
    print(description)

    # Check if a stock object with the same name already exists
    stocks = Stock.objects.filter(stock_symbol=stock_id)
    if stocks.exists():
        stock = stocks.first()  # Fetch the first matching Stock object
        prev = stock.current_price
        stock.previous_price = prev
    else:
        stock = Stock(stock_symbol=stock_id)  # Create a new Stock object
        stock.previous_price = 'N/A'

    # Update other fields
    stock.name = name
    stock.current_price = price
    stock.fiftytwo_week_range = fiftytwo_week_range
    stock.market_cap = market_cap
    stock.pe_ratio = pe_ratio
    stock.earnings_date = earnings_date
    stock.sector = sector
    stock.industry = industry
    stock.full_time_employees = full_time_employees
    stock.description = description
    stock.save()

    driver.execute_script("window.scrollTo(0, 0);")

    # Navigate to historical data 
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="nimbus-app"]/section/section/aside/section/nav/ul/li[6]/a'))).click()

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 14);")

    time.sleep(2)

    table = driver.find_element(By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/div[1]/div[3]/table')
    rows = table.find_elements(By.XPATH, ".//tbody/tr")

    # Extract each row's data
    for row in rows:
        columns = row.find_elements(By.XPATH, ".//td")
        if len(columns) >= 7:
            date = columns[0].text
            if date[4] == '1' and date[5] == ',':
                open = columns[1].text
                high = columns[2].text
                low = columns[3].text
                close = columns[4].text
                adj_close = columns[5].text
                volume = columns[6].text

                # Check if a hist data object with the same name already exists
                data = HistoricalData.objects.filter(stock_symbol=stock_id, date=date)
                if data.exists():
                    this = data.first()  # Fetch the first matching Stock object
                else:
                    this = HistoricalData(stock_symbol=stock_id)

                # Update other fields
                this.date = date
                this.open = open
                this.close = close
                this.high = high
                this.low = low
                this.adj_close = adj_close
                this.volume = volume
                this.save()

                print(date)
                print(open)
                print(close)
                print(high)
                print(low)
                print(adj_close)
                print(volume)

    driver.quit()