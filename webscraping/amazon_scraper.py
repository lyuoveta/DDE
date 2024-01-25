from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver import Firefox, Chrome
import pandas as pd
import re
from bs4 import BeautifulSoup as bs

def get_max_reviews(asin):

    amazon_url_top = 'https://www.amazon.com/product-reviews/' + \
                    asin + \
                    '/ref=cm_cr_arp_d_viewopt_srt?reviewerType=all_reviews&sortBy=helpful&pageNumber=1'
    amazon_url_recent = 'https://www.amazon.com/product-reviews/' + \
                    asin + \
                    '/ref=cm_cr_arp_d_viewopt_srt?reviewerType=all_reviews&sortBy=recent&pageNumber=1'
    
    url_list = [amazon_url_top, amazon_url_recent]

    return url_list

def scraper(url):

    driver = Firefox()
    driver.maximize_window()
    driver.get(url)

    product_data = {'product_name': [driver.find_elements(By.XPATH, '//a[@data-hook="product-link"]')[0].text],
                    'total_ratings': [driver.find_elements(By.XPATH, '//span[@data-hook="rating-out-of-text"]')[0].text.split()[0].replace('.', ',')],
                    'number_reviews': [driver.find_elements(By.XPATH,'//div[@data-hook="cr-filter-info-review-rating-count"]')[0].text.split()[3].replace(',', '')]}

    reviews_data = {'review_dates': [i.text.split('on')[-1] for i in driver.find_elements(By.XPATH, "//span[@data-hook='review-date']")],
                    'review_places': [i.text.split('on')[0].split('the')[-1] for i in driver.find_elements(By.XPATH, "//span[@data-hook='review-date']")],
                    'review_ratings': [i.get_attribute('textContent')[0] for i in driver.find_elements(By.XPATH, "//i[@data-hook='review-star-rating']/span")],
                    'review_authors': [i.text for i in driver.find_elements(By.CSS_SELECTOR, '#cm_cr-review_list .a-profile-name') if i.text != ''],
                    'review_titles': [i.text for i in driver.find_elements(By.XPATH, "//a[@data-hook='review-title']/span") if i.text != ''],
                    'reviews': [i.text for i in driver.find_elements(By.XPATH, '//span[@data-hook="review-body"]')]}        

    for page in range(9):
        try:
            next_btn = driver.find_element(By.XPATH, "//ul[@class='a-pagination']/li[2]/a")
            next_btn.click()
            time.sleep(5)
        except Exception as ex:
            break
        
        reviews_data['review_dates'].extend([i.text.split('on')[-1] for i in driver.find_elements(By.XPATH, "//span[@data-hook='review-date']")])
        reviews_data['review_places'].extend([i.text.split('on')[0].split('the')[-1] for i in driver.find_elements(By.XPATH, "//span[@data-hook='review-date']")])
        reviews_data['review_ratings'].extend([i.get_attribute('textContent')[0] for i in driver.find_elements(By.XPATH, "//i[@data-hook='review-star-rating']/span")])
        reviews_data['review_authors'].extend([i.text for i in driver.find_elements(By.CSS_SELECTOR, '#cm_cr-review_list .a-profile-name') if i.text != ''])
        reviews_data['review_titles'].extend([i.text for i in driver.find_elements(By.XPATH, "//a[@data-hook='review-title']/span") if i.text != ''])
        reviews_data['reviews'].extend([i.text for i in driver.find_elements(By.XPATH, '//span[@data-hook="review-body"]')])

    # df_product = pd.DataFrame(product_data).reindex(range(100)).ffill()

    df_reviews = pd.DataFrame(reviews_data)

    # df_full = pd.concat([df_product, df_reviews], axis=1, sort=False)

    driver.close()
    return df_reviews

def core(asin_list):
    try:
        for asin in asin_list:
            print(f"IN PROCESS FOR: {asin}")
            url_list = get_max_reviews(asin)
            df_main = pd.DataFrame()
            for url in url_list:
                df_new = scraper(url)
                df_main = pd.concat([df_main, df_new])
            df_main.to_csv(f'{asin}.csv', encoding='utf-8', index=False)
            print(f'Success download {asin} file in root directory')
    except Exception as e:
        return f'Error: {e}'
    
asin_list = ['B009SZXM4E','B002EA99HE', 'B000OA6Z6O', 'B07GSGWZMB', 'B07S38C5WW']
core(asin_list)