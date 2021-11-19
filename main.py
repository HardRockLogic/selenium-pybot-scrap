import math
import numpy as np

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests


def getData(url='https://md-fashion.com.ua/store/man/obuv/krossovki/under-armour', update=False, price_range_flag=False):

    if update:
        options = webdriver.ChromeOptions()

        # add user agent
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/95.0.4638.69 Safari/537.36")

        # disable webDriver mode
        options.add_argument("--disable-blink-features=AutomationControlled")

        # enter a headless mode to avoid rendering browser window
        options.headless = True

        driver = webdriver.Chrome(
            executable_path="C:\\Users\\Legion\\Documents\\mdFashionScrap\\chromedriver.exe",
            options=options
        )

        try:
            driver.get(url)
            button = driver.find_element(By.XPATH, "//a[@class='btn btn--accent']")

            amount_of_filtered_items = int(button.get_attribute('data-filter-result'))
            limit_of_items = int(button.get_attribute('data-items-on-page-limit'))

            times_btn_click = math.ceil(amount_of_filtered_items / limit_of_items)
            print(times_btn_click)

            times_btn_click -= 1

            while times_btn_click != 0:
                button.click()
                time.sleep(2)
                times_btn_click -= 1

            new_page = driver.page_source #encode('utf-8')

        except Exception as ex:
            print(ex)

        finally:
            driver.close()
            driver.quit()

        with open('sneakers.html', 'w', encoding='utf-8') as file:
           file.write(new_page)

    with open('sneakers.html', encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    sneakers = soup.find_all('span', class_='sale')

    img_urls = []
    sneaker_params = {}

    for sneaker in sneakers:
        sneak_url = sneaker.find_previous().get('data-href')
        price = sneaker.get('data-price')
        name = sneaker.find_previous().text
        img_url = sneaker.find_previous('picture').find('source').get('data-srcset')
        intermediate = img_url.split(' ')
        sneaker_params[sneak_url] = (price, name, intermediate[2])

    if price_range_flag is not False:
        if price_range_flag[0]:
            sneaker_params = {key: value for key, value in sneaker_params.items()
                              if price_range_flag[1][0] <= int(value[0]) <= price_range_flag[1][1]}


    return sneaker_params

getData('https://md-fashion.com.ua/store/man/obuv/krossovki/under-armour')

# Url address with active size filter (but there is an issue occurs when tying to find half sizes snickers like 10,5
# its showing nothing although there are available items in store) >>>
# https://md-fashion.com.ua/store/man/obuv/krossovki/nizkie-krossovki/under-armour/10


def filter_size_by_url(size):
    url = f'https://md-fashion.com.ua/store/man/obuv/krossovki/nizkie-krossovki/under-armour/{size}'
    return url


def main():
    getData('https://md-fashion.com.ua/store/man/obuv/krossovki/under-armour')
    # TODO: 1. add size filtering to getData in advance;
    #   2. resolve problem with factorial sizes like 10-5 etc.;


if __name__ == '__main__':
    main()
