from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
from datetime import datetime
import pandas as pd
import unicodedata
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
driver.get("https://www.vivino.com/HK/en/")


########################################################################################################################
# switch to targeted place
def mouse_over(driver, selector):
    element_to_hover_over = driver.find_element(By.CSS_SELECTOR, selector)
    hover = ActionChains(driver).move_to_element(element_to_hover_over)
    hover.perform()


mouse_over(driver, '.navigationItem__labelContainer--21d49 span[title="Regions"]')
driver.find_element(By.CSS_SELECTOR, '.subMenu__section--2x0LR span[title="France"]').click()

# starting_point = driver.find_element(By.CSS_SELECTOR, '.rc-slider .rc-slider-handle.rc-slider-handle-1')
# location_1 = starting_point.location
# print(location_1)
#
# end_point = driver.find_element(By.CSS_SELECTOR, '.rc-slider .rc-slider-handle.rc-slider-handle-2')
# location_2 = end_point.location
# print(location_2)
#
# bar = driver.find_element(By.CSS_SELECTOR, ".rc-slider-track.rc-slider-track-1")
# location_3 = bar.location
# print(location_3)

time.sleep(3)
price_range = driver.find_element(By.CSS_SELECTOR, '.filterByPriceRange__header--Ud3Hg')
driver.execute_script("arguments[0].scrollIntoView();", price_range)

starting_point = driver.find_element(By.CSS_SELECTOR, '.rc-slider .rc-slider-handle.rc-slider-handle-1')
end_point = driver.find_element(By.CSS_SELECTOR, '.rc-slider .rc-slider-handle.rc-slider-handle-2')
time.sleep(5)
move = ActionChains(driver)
move.drag_and_drop_by_offset(starting_point, -29, 0).perform()
time.sleep(5)
move.drag_and_drop_by_offset(end_point, 337, 0).perform()
time.sleep(5)


########################################################################################################################
# every scroll-down could show 25 products, adding 10 as precautionary measures

def scroll_down(target_number_down):
    find_number = target_number_down.split(" ")
    numbers_of_item = int(find_number[1])
    loop_times = 1
    # loop_times = int((numbers_of_item / 25) + 10)
    scrolling_up = driver.find_element(By.CSS_SELECTOR, '.querySummary__querySummary--39WP2')

    for x in range(loop_times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(4.5)
        driver.execute_script("return arguments[0].scrollIntoView(true);", scrolling_up)
        time.sleep(0.5)


########################################################################################################################
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii


########################################################################################################################

all_products = []
all_products_without_name = []


def webscrapping(real_time, webpage, region_name):
    # all_products = []
    # all_products_without_name = []

    find_table = driver.find_element(By.CSS_SELECTOR, ".explorerPage__results--3wqLw")
    all_wine = find_table.find_elements(By.CSS_SELECTOR, ".wineCard__topSection--11oVj")
    for wine in all_wine:
        garden = wine.find_element(By.CSS_SELECTOR, ".wineInfoVintage__truncate--3QAtw").get_attribute("textContent")
        clear_garden_name = str(remove_accents(garden), encoding="utf8")
        wine_name = wine.find_element(
            By.CSS_SELECTOR,
            ".wineInfoVintage__vintage--VvWlU.wineInfoVintage__truncate--3QAtw"
        ).get_attribute("textContent")
        clear_wine_name = str(remove_accents(wine_name), encoding="utf8")
        location = wine.find_element(
            By.CSS_SELECTOR,
            ".wineInfoLocation__regionAndCountry--1nEJz"
        ).get_attribute("textContent")
        clear_location = str(remove_accents(location), encoding="utf8")
        time.sleep(1)
        price = wine.find_element(By.CSS_SELECTOR, ".addToCartButton__price--qJdh4").get_attribute("textContent")

        sub_list_01 = clear_wine_name.split(" ")
        year = ""
        for elements in sub_list_01:
            elements.split(" ")
            if elements[-4:].isdigit():
                year = str(elements[-4:])
            else:
                year = "N/A"
        name = " ".join([item for item in sub_list_01 if not item.isdigit()])

        sub_list_02 = clear_location.split(", ")
        sub_division = sub_list_02[0]
        country = sub_list_02[1]

        final_price = int(price.replace(", ", "").replace("HK$", "").replace(",", ""))

        all_products.append(
            [real_time, webpage, country, region_name, sub_division, year, clear_garden_name, final_price, name]
        )
        all_products_without_name.append(
            [real_time, webpage, country, region_name, sub_division, year, clear_garden_name, final_price]
        )

        if region_name == "Bourgogne":
            region_name = "Burgundy"

        print(all_products)
    # return all_products, all_products_without_name


########################################################################################################################

today = datetime.today()
real_time = today.strftime("%Y/%m/%d")

webpage = 'Vivino'

scrolling_down = driver.find_element(By.CSS_SELECTOR, '.filterPills__header--1kcAC')
driver.execute_script("return arguments[0].scrollIntoView();", scrolling_down)
time.sleep(8)

whole_table = driver.find_element(By.CSS_SELECTOR, ".explorerPageFilters__filters--2_MsE")
region_menu = whole_table.find_elements(By.CSS_SELECTOR, "div")
buttons = []
for reg in region_menu:
    if 'Regions' in reg.get_attribute("textContent"):
        print(reg.get_attribute("textContent"))
        buttons = reg.find_elements(By.CSS_SELECTOR, ".pill__inner--2uty5")
    for button in buttons:
        region_name = button.get_attribute("textContent")
        button.click()
        target = driver.find_element(By.CSS_SELECTOR, '.querySummary__querySummary--39WP2').get_attribute("textContent")
        scroll_down(target)
        print('scrolling is complete')
        time.sleep(1)
        webscrapping(real_time, webpage, region_name)
        time.sleep(1)
        button.click()

driver.quit()
print("scrapping done")

########################################################################################################################

today_for_df = datetime.today()
now_time_for_df = today_for_df.strftime("%Y-%m-%d")

all_data = pd.DataFrame(
    all_products,
    columns=['Date', 'Webpage', 'Country', 'Region', 'Subdivision', 'Year', 'Garden', 'Price', 'Name_of_wine']
)
all_data.to_csv(f'France_wine_vivino_with_name_{now_time_for_df}.csv', index=False)

all_data_without_name = pd.DataFrame(
    all_products_without_name,
    columns=['Date', 'Webpage', 'Country', 'Region', 'Subdivision', 'Year', 'Garden', 'Price']
)
all_data_without_name.to_csv(f'France_wine_vivino_without_name_{now_time_for_df}.csv', index=False)
########################################################################################################################
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
    #
    #     # loop through the data frame
    #     for i, row in all_data_without_name.iterrows():
    #         # here %S means string values
    #         sql = "INSERT INTO France_wine_final.France_wine_final VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    #         cursor.execute(sql, tuple(row))
    #         print("Record inserted")
    #         # the connection is not auto committed by default, so we must commit to save our changes
    #         conn.commit()
    #
    #     for i, row in all_data.iterrows():
    #         # here %S means string values
    #         sql = "INSERT INTO France_wine_final.France_wine_with_name_shown VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    #         cursor.execute(sql, tuple(row))
    #         print("Record inserted")
    #         # the connection is not auto committed by default, so we must commit to save our changes
    #         conn.commit()
except Error as e:
    print("Error while connecting to MySQL", e)
