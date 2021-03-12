# Scraping action.com using Selenium
# There needs to be installed chromedriver.exe in the same folder where the script is run
# python 3.6 running on Windows 10 32-bit

import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime


class Scraper(object):
    ''' A lot of the messy code is just playing with the tags from the page'''

    def __init__(self, link):
        self.link = link
        self.driver = self.configure_driver()  # The simulated browser
        self.keys = ['name', 'price']  # We will scrape those in the same way, the rest will go sepparately
        self.selectors = [  # The selectors for the name and price, respectively
            'header[class="product-details__header"]>h2',
            'div[class="v-price product-price__full"]',  
        ]
        self.data = {  # A dictionary with all the data
            'product_url': self.link
        }

    # Configuring the browser simulator, named driver, that will get all the information
    def configure_driver(self):
        # Add additional Options to the webdriver
        chrome_options = Options()
        # add the argument and make the browser Headless. It will work smoother, faster but it will miss the first category
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options = chrome_options)
        # Basically we simulate a browser accesing the website
        return driver
        
    # Extracting the text from the website elements/tags
    def get_element_info(self, selector):  # Scraping each element
        element_tag = self.get_tag(selector)
        clean_tag_text = element_tag.text.replace('\n', '')  # To clear the price
        return clean_tag_text

    def get_tag(self, selector):  # Returns the tag that we are looking for
        try:  # This tells the driver to wait for the element 10 sec to appear
            return WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        except TimeoutException:
            print("The Website doesn't cooperate! Can't find elements")

    # The 'main' function for the app
    def run(self):
        with self.driver:  # Context manager that will close the driver when we are done
            self.driver.get(self.link)  # Accesing the link
            for index, key in enumerate(self.keys):  # Finding the product name, price
                current_selector = self.selectors[index]
                self.data[key] = self.get_element_info(current_selector)

            # Getting the product ID
            id_css_selector = 'table[class="specifications-table"]'
            all_properties = self.get_tag(id_css_selector).text.split('\n')  # All the properties, bellow the img
            for prop in all_properties:  # Extracting the ID from all the properties
                name, value = prop.split()
                if name == 'Artikelnummer':
                    id = value  # Assigning the id
                    break
            self.data['id'] = id

            # Extracting the image url
            image_css_selector = '.media-slider__media > ol:nth-child(1) > li:nth-child(1) > button:nth-child(1) > div:nth-child(1) > picture:nth-child(1) > img:nth-child(4)'
            # The url is found in the 'srcset' attribute of the 'img' tag, near some other attributes,so we split and extract only the url
            img_url = self.get_tag(image_css_selector).get_attribute('srcset').split('?')[0]
            self.data['image_url'] = img_url

            # Getting the datetime
            self.data['datetime'] = datetime.now().strftime("%d-%m-%Y %H:%M")

            # Getting the categories
            try:  # Getting the first category might throw and error if the page doesn't have it
                first_category = self.get_tag('ol.page-header__nav__panel__menu:nth-child(1) > li:nth-child(4) > a:nth-child(1)').text  # Accessing the tag with the first category
                self.data['Category 1'] = first_category
            finally:
                all_categories = self.driver.find_elements_by_css_selector('span.name')
                for i, category in enumerate(all_categories[1:-1]):  # Skiping the first/last category, as they just show the home page and the product
                    self.data[f'Category {i+2}'] = category.text  # Adding the category to our 'data' dict

if __name__ == '__main__':
    product_link = 'https://www.action.com/nl-nl/p/redmax-shaping-sportbroek-/'  # An example of a product
    app = Scraper(product_link)
    app.run()
    print(app.data)