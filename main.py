from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time


search_phrase = "War"
options = webdriver.FirefoxOptions()

# Function to scroll to position of 'Show More' Button. 
# Total result set after clicking 'Show More' = 20
def scroll_shim(passed_in_driver, object):
    x = object.location['x']
    y = object.location['y']
    scroll_by_coord = 'window.scrollTo(%s,%s);' % (
        x,
        y
    )
    scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
    passed_in_driver.execute_script(scroll_by_coord)
    passed_in_driver.execute_script(scroll_nav_out_of_way)




options.add_argument('--ignore-certificate-errors-spki-list')
options.add_argument('--ignore-ssl-errors')

service = Service(executable_path="geckodriver.exe")
driver = webdriver.Firefox(service=service, options=options)


driver.get("https://www.aljazeera.com/")

driver.maximize_window()

# Find and click search button
buttons = driver.find_elements('xpath', '//button[.//span[text()[contains(., "Click here to search")]]]')

for btn in buttons:
    btn.click()
    break

#Enter search term into input field
inputBar = driver.find_element(By.CLASS_NAME, "search-bar__input")
inputBar.send_keys(search_phrase + Keys.ENTER)

# Select Date category
dropdown = WebDriverWait(driver, 50).until(
    EC.presence_of_element_located((By.CLASS_NAME, "search-summary__select"))
)
dropdown.click()

dropdown_options = WebDriverWait(driver, 50).until(
    EC.presence_of_all_elements_located((By.TAG_NAME, "option"))
)
print(dropdown_options)

i = 0
while i < len(dropdown_options):
    if(dropdown_options[i].text == "Date"):
        dropdown_options[i].click()
        break
    i = i + 1


# Scroll down and Press show more button
show_more_btn = WebDriverWait(driver, 60).until(
    EC.presence_of_element_located(('xpath', '//button[.//span[text()[contains(., "Click here to show more content")]]]'))
)

if 'firefox' in driver.capabilities['browserName']:
    scroll_shim(driver, show_more_btn)

ActionChains(driver).move_to_element(show_more_btn).click().perform()

time.sleep(10)
articles = driver.find_elements(By.TAG_NAME, 'article')

# WebDriverWait(driver, 360).until(
#     EC.presence_of_all_elements_located((By.TAG_NAME, 'article'))
# )

print(articles)
# //article[@class="gc u-clickable-card gc--type-customsearch#result gc--list gc--with-image"]
# driver.find_elements('xpath', '//article[@class="gc u-clickable-card gc--type-customsearch#result gc--list gc--with-image"]')

news_items = []
title = []
desc = []
date = []
count = []
money = []
image_url = []

j = 0
while j < len(articles):
    ttl = articles[j].find_element('xpath', './/h3[@class="gc__title"]//span').get_attribute('innerHTML').replace('\n', '')
    title.append(ttl)
    string_list = articles[j].find_element('xpath', './/div[@class="gc__excerpt"]//p').text.split('...')
    desc.append(string_list[1].replace('\n', ''))
    date.append(string_list[0])
    count.append(ttl.count(search_phrase) + string_list[1].count(search_phrase))
    money.append(True if(ttl.find('$' or 'dollars' or 'USD') != -1 or string_list[1].find('$' or 'dollars' or 'USD') != -1)
                 else False)
    image_url.append(articles[j].find_element('xpath', './/img[@class="article-card__image gc__image"]').get_attribute('src'))
    j = j + 1

dframe = pd.DataFrame({'title':title, 'description': desc, 'date': date, 'search_phrase count': count, 'currency': money, 'iamge_url': image_url.})

print(dframe)

# time.sleep(50)

# driver.quit()