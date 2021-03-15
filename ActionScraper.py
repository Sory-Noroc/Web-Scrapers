# Scraping action.com using Selenium
# There needs to be installed chromedriver.exe in the same folder where the script is run
# python 3.6.8 running on Windows 10 32-bit

import sys, csv, os, re, threading
from selenium import webdriver  # Selenium 3.141.0
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from multiprocessing.pool import Pool
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep


class Scraper:
    ''' The main class, runs the whole program '''

    def __init__(self, link, cs, ps):
        self.link = link
        self.driver = self.configure_driver()  # The simulated browser
        self.categories_url = []  # A list of categories, ex. Dieren, Decoratie
        self.category_selector = cs
        self.product_selector = ps
        self.keys = ['name', 'price']  # We will scrape those in the same way, the rest will go sepparately
        self.selectors = [  # The selectors for the name and price, respectively
            'header[class="product-details__header"]>h2',
            'div[class="v-price product-price__full"]',  
        ]
        self.data = {}  # A dictionary with all the data
        self.local_thread = threading.local()  # For threading

    # Configuring the browser simulator, named driver, that will get all the information
    def configure_driver(self):
        try:
            # Add additional Options to the webdriver
            chrome_options = Options()
            # add the argument and make the browser Headless. It will work smoother& faster but it will miss the first category
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--log-level=OFF")
            driver = webdriver.Chrome(options = chrome_options)
            return driver
        except Exception as e:
            print(e, 'Install chromedriver.exe depending on chrome version, add it to CWD and try again')
            sys.exit(0)

    # This will create drivers for each process (multithreading)
    def get_driver(self):
        driver = getattr(self.threadLocal, 'driver', None)
        if driver is None:
            driver = self.configure_driver()
            setattr(threadLocal, 'driver', driver)
        return driver

    def getUrlDomain(self, link):  # Returns only the domain from full link, ex. action.com
        domain = urlparse(page_link).netloc
        return domain

    # Clicks the provided element from the page, waits for it to appear if not visible
    def click_element(self, selector, by=By.CSS_SELECTOR):
        try:  # Waits for the element to appear on the page
            element = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((by, selector)))
            ActionChains(self.driver).move_to_element(element).click(element).perform()
        except TimeoutException:
            print("Element Not found")

    # Extracting the text from the website elements/tags
    def get_element_info(self, selector):  # Scraping each element
        element_tag = self.get_tag(selector)
        clean_tag_text = element_tag.text.replace('\n', '')  # To clear the price
        return clean_tag_text

    # Returns the tag/s that we are looking for
    def get_tag(self, selector, by=By.CSS_SELECTOR, all=False):
        try:  # This tells the driver to wait for the element 10 sec to appear
            if not all:  # If we requested only one element
                return WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by, selector)))
            else:  # If we want all the elements
                return WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((by, selector)))
        except TimeoutException:
            print("The Website doesn't cooperate! Can't find elements")

    # Clicks the first category found, for ex. Decoratie,Dieren,etc
    def get_category_page(self):
        self.click_element(self.category_selector, By.XPATH)
        self.categories_url.append(self.driver.current_url)

    # Clicks the first product found in thee category
    def get_product_page(self, selector):
        self.click_element(selector)
        self.data['product_url'] = self.driver.current_url

    # Finds then returns the link for every category
    def get_category_links(self):
        with self.driver:  # Context manager that will close the driver when we are done
            self.driver.get(self.link)  # Accesing the link
            # Storing the links to all the categories
            d = self.getUrlDomain(self.link)  # The domain of the wesite
            categ_hrefs = [urljoin(d,i.get_attribute('href')) for i in self.get_tag(
                self.category_selector, by=By.XPATH, all=True)]
        return categ_hrefs

    def get_products(self, url):
        driver = self.get_driver()
        driver.get(url)  # Accessing the category link
        try:
            i = 1
            while True:  # We loop over all the products, accessing one by one
                selector = f'{self.product_selector}[{i}]'
                product = self.get_tag(selector, By.XPATH)
                product.click()  # Accessing each product
                self.get_product_info()  # Does the heavy work of extracting everything about the product
                self.write2csv()
                # Going back to all products after scraping one of them
                driver.execute_script("window.history.go(-1)")
                i+=1
        except Exception as e:
            print(e, 'Finished products')

    def get_product_info(self):
        # Finding the product name, price
        print('Scraping product')
        for index, key in enumerate(self.keys):  
            current_selector = self.selectors[index]
            self.data[key] = self.get_element_info(current_selector)

        # Getting the product ID
        id_css_selector = 'table[class="specifications-table"]'
        all_properties = self.get_tag(id_css_selector).text.split('\n')  # All the properties, bellow the img
        for prop in all_properties:  # Extracting the ID from all the properties
            if 'Artikelnummer' in prop:  # If its the id property
                name, value = prop.split()
                id = value  # Assigning the id
                break
        self.data['id'] = id

        # Extracting the image url
        image_css_selector = '.media-slider__media > ol:nth-child(1) > li:nth-child(1) > button:nth-child(1) > div:nth-child(1) > picture:nth-child(1) > img:nth-child(4)'
        # The url is found in the 'srcset' attribute of the 'img' tag, near some other so we split and extract only the url
        img_url = self.get_tag(image_css_selector).get_attribute('srcset').split('?')[0]
        self.data['image_url'] = img_url

        # Extracting the barcode
        code_pattern = re.compile(r'[\d]{13}')
        try:
            barcode = re.findall(code_pattern, img_url)[0]  # Extracting the bar from the img_url
        except IndexError:  # If couldn't find a 13 digit code inside the img url
            print("Couldn't extract barcode")
            barcode = ''
        self.data['barcode'] = barcode

        # Getting the datetime
        self.data['datetime'] = datetime.now().strftime("%d-%m-%Y %H:%M")

        # Getting the categories
        first_category = self.get_tag('ol.page-header__nav__panel__menu:nth-child(1) > li:nth-child(4) > a:nth-child(1)').text  # Accessing the tag with the first category
        if first_category:  # If the driver found the first category
            self.data['Category 1'] = first_category
        all_categories = self.driver.find_elements_by_css_selector('span.name')
        for i, category in enumerate(all_categories[1:-1]):  # Skiping the first/last category, as they just show the home page and the product
            self.data[f'Category {i+2}'] = category.text  # Adding the category to our 'data' dict

        # Adding the urls
        self.data['category_url'] = self.categories_url[0]
        self.data['product_url'] = self.driver.current_url
        
    def write2csv(self):
        csv_name = 'scrapedData.csv'
        with open(csv_name, 'a', encoding='utf8', newline='') as file:
            csv_writer = csv.writer(file, delimiter=',')
            if os.stat(csv_name).st_size == 0:  # If the file is empty, we write the headers
                csv_writer.writerow(self.data.keys())  # Writing the criterias, first line
            csv_writer.writerow(self.data.values())  # Writing the data values

    # The 'main' function for the app
    def run(self):
        category_urls = self.get_category_links()
        print(category_urls)
        Pool().map(self.get_products, category_urls)  # This starts and maintains the processes

if __name__ == '__main__':
    page_link = 'https://www.action.com/nl-nl/click-and-collect-producten/'
    category_css = "//section[@class='grid']//div[@class='grid-item grid-item--content']/a"
    product_css = "(//section[@class='grid']//a[@class='product-card__link'])" 
    app = Scraper(page_link, category_css, product_css)
    app.run()
    app.driver.quit()
