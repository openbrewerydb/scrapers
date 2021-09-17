from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from time import sleep
from datetime import date
import sys
import pandas as pd
import json
# import paths


options = webdriver.ChromeOptions()
options.add_argument ("lang=en_us")
options.page_load_strategy = 'eager'
# options.add_argument('--disable-blink-features=AutomationControlled')
# options.add_argument("--headless")
driver = webdriver.Chrome(executable_path='/home/juicobowley/repos/tx-cbg-scraper/chromedriver', options = options)
driver.get('chrome://settings/')
driver.execute_script('chrome.settingsPrivate.setDefaultZoom(0.25);')

# driver.set_window_position(-1275, 345)
# driver.set_window_size(1080,800)
# driver.minimize_window()

def csss(parent, sel):
    return parent.find_elements_by_css_selector(sel)
def css(parent, sel):
    return parent.find_element_by_css_selector(sel)
def xpaths(parent, sel):
    return parent.find_elements_by_xpath(sel)
def xpath(parent, sel):
    return parent.find_element_by_xpath(sel)


def make_item_row():
    item_row = {}
    item_row['brewery_name'] = None
    item_row['address'] = None
    item_row['brewery_page_url'] = None
    item_row['list_order'] = None
    return item_row

def make_brewery_row():
    brewery_row = {}
    brewery_row['brewery_url'] = None
    brewery_row['brewery_phone'] = None
    brewery_row['brewery_coordinates'] = None
    brewery_row['list_order'] = None
    return brewery_row


items = []
brewerys = []
def update_show_count():
    show_all_id_selector = '#pp_show_all'
    show_100_id_selector = '#pp_100'
    else_show_100_selector = 'div.hawk-viewNumber select option[value="100"]'
    sleep(0.5)
    try:
        if len(csss(driver, show_all_id_selector)) > 0:
            css(driver, '#per_page_select').click()
            print('\nUpdating show count to ALL\n')
            css(driver, show_all_id_selector).click()
        elif len(csss(driver, show_100_id_selector)) > 0:
            css(driver, '#per_page_select').click()
            print('\nUpdating show count to 100 with ID\n')
            css(driver, show_100_id_selector).click()
        else:
            print('\nUpdating show count to 100 with attribute\n')
            css(driver, else_show_100_selector).click()
    except:
        print('\nFailed to update show count\n')

def identify_feature(dict_feature, parent, selector):
    try:
        dict_feature = css(parent, selector)
        print(dict_feature.text)
    except StaleElementReferenceException:
        print(f'StaleElementReferenceException while trying grab {dict_feature}, trying to find element again')
        dict_feature = css(parent, selector)
        print(dict_feature.text)
    return dict_feature

def scrape_items(url, page):
    list_order = 0
    # update_show_count()
    print('\t Entered scraper function')
    # sleep(10)
    for item in csss(driver, 'div#SFylpcrd > a'):
        print(item)
        list_order += 1
        item_row = make_item_row()
        try:
            item_row['brewery_name'] = identify_feature(item_row['brewery_name'], item, '.SFcrdnam').text
        except:
            print("Couldn't get brewery name")
        try:
            item_row['address'] = identify_feature(item_row['address'], item, 'div>div:nth-child(2)').text.replace('\n', ' ')
        except:
            print("Couldn't get brewery address")
        try:
            # item_row['brewery_page_url'] = identify_feature(item_row['brewery_page_url'], item, '.SFcrd').get_attribute('href')
            item_row['brewery_page_url'] = item.get_attribute('href')
        except:
            print(f"Couldn't get brewery page url")
        # item_row['origin_url'] = url
        # item_row['site_name'] = "Abt"
        # item_row['list_order'] = list_order
        item_row['page_num'] = page


        print(item_row)
        items.append(item_row)
    return items
    
def scrape_individual_breweries(url):
    list_order = 0
    list_order += 1
    brewery_row = make_brewery_row()
    
    try:
        brewery_row['brewery_url'] = identify_feature(brewery_row['brewery_url'], driver, '.SFbizctcweb').get_attribute('href')
    except:
        print(f"Couldn't get brewery page url")
    try:
        brewery_row['brewery_phone'] = identify_feature(brewery_row['brewery_phone'], driver, '.SFbizctcphn').text
    except:
        print(f"Couldn't get brewery phone")
    try:
        brewery_row['brewery_coordinates'] = identify_feature(brewery_row['brewery_coordinates'], driver, 'div#SFbizmap').get_attribute('data-loc')
    except:
        print(f"Couldn't get brewery coordinates")
    print(brewery_row)
    brewerys.append(brewery_row)
    return brewerys
            
    # click_next_page(url, page)
# //a[contains(@class, 'pure-button-primary pure-button-disabled')]/following::a
# def click_next_page(url, page):
#     next_button_selector = "//div[@id='hawkbottompager']//span[@class='hawk-pageActive']/following::a[@class='hawk-pageLink']"
#     if len(xpaths(driver, next_button_selector)) > 0:
#         click_attempt = 0
#         while click_attempt < 2:
#             try:
#                 driver.execute_script("window.scrollTo(0, -200);")
#                 sleep(1)
#                 print('#####  trying to click next page')
#                 next_page = xpath(driver, next_button_selector).get_attribute('href')
#                 print (next_page)
#                 driver.get(next_page)
#                 sleep(10)
#                 scrape_items(url, page + 1)
#             except:
#                 print("error\nretrying")
#                 click_attempt += 1
#                 print(click_attempt)
#             finally:
#                 return





urls = [
    'https://texascraftbrewersguild.org/directory-brewery-members/#!directory/map',
    ]

# go to all links and scrape information
site = 'Texas Craft Brewers Guild'

url_count = 0
for url in urls:
    url_count += 1
    print('Getting URL')
    driver.get(url)
    sleep(5)
    scrape_items(url, 1)
    print(f"\nNavigating to url # {str(url_count)} out of {len(urls)}: {url}\n ")
df = pd.DataFrame(items)
df.to_csv('tx-cbg.csv')

for brewery in items:
    print(brewery)
    driver.get(brewery['brewery_page_url'])
    sleep(2)
    print(f"reached {brewery['brewery_page_url']}")
    scrape_individual_breweries(url)
df2 = pd.DataFrame(brewerys)
df2.to_csv('brewery_info.csv')

# just a few quality of life things for myself for when the program finishes
print(df.head())
print(f'\n\n###############\n\n{df["brewery_name"].count()} items scraped\n\n###############\n\n')
print('Exporting df to csv')

print('Closing in 3')
sleep(3)

    
driver.quit()
sys.exit()