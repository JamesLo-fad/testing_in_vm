# The following exchange rate is provided with the X-RATES Website.
########################################################################################################################

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import pandas as pd
from datetime import datetime
import mysql.connector as msql
from mysql.connector import Error


s = Service(GeckoDriverManager().install())
firefox_options = Options()
firefox_options.add_argument("--headless")
firefox_options.add_argument("--disable-extensions")
firefox_options.add_argument("--disable-gpu")
firefox_options.add_argument("--disable-dev-shm-usage")
firefox_options.add_argument("--no-sandbox")

driver = webdriver.Firefox(service=s, options=firefox_options)
driver.get("https://www.x-rates.com/table/?from=HKD&amount=1")

all_data = []


def webscrapping(real_time, webpage):
    find_table = driver.find_element(By.CSS_SELECTOR, ".ratesTable")
    exchange_rate = find_table.find_elements(By.CSS_SELECTOR, ".ratesTable tbody tr")
    for rates in exchange_rate:
        dollar_name = rates.find_element(By.CSS_SELECTOR, "td").get_attribute("textContent")
        pick_inverse = rates.find_element(By.CSS_SELECTOR, "td:nth-child(3)").get_attribute("textContent")

        all_data.append([real_time, webpage, dollar_name, pick_inverse])

        print(all_data)


today = datetime.today()
real_time = today.strftime("%Y/%m/%d")
now_time_for_df = today.strftime("%Y-%m-%d")

webpage = 'X-RATES'

webscrapping(real_time, webpage)

driver.quit()
print("scrapping done")

# pd to csv

all_rates = pd.DataFrame(
    all_data,
    columns=['Date', 'Webpage', 'Currency_name', 'Currency_rate']
)
all_rates.to_csv(f'Forex_rate_{now_time_for_df}.csv', index=False)

print('Done!')

# SQL  Part

try:
    print('Connecting to the MySQL...........')
    conn = msql.connect(
        host='34.92.158.101',
        user='root',
        password='joniwhfe',
        database='France_wine_final'
    )
    if conn.is_connected():
        print("Connection successfully..................")
        cursor = conn.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)

        # # loop through the data frame
        # for i, row in all_rates.iterrows():
        #     # here %S means string values
        #     sql = "INSERT INTO France_wine_final.Everyday_exchange_rate VALUES (%s,%s,%s,%s)"
        #     cursor.execute(sql, tuple(row))
        #     print("Record inserted")
        #     # the connection is not auto committed by default, so we must commit to save our changes
        #     conn.commit()

except Error as e:
    print("Error while connecting to MySQL", e)
