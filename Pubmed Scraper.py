# Python 3.6
# This scraper extracts data like emails from a dynamic page, using selenium and saves it to csv

import re
import csv
import selenium
from time import sleep
from selenium import webdriver, common
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.proxy import *

def findEmail(driver):  # This function searches for the email on the page
	try:
		expand_button = driver.find_element_by_id("toggle-authors")
		expand_button.click()
		email_text = driver.find_element_by_id("full-view-expanded-authors").text
		return email_text  # Returning the text from the tag, which contains the emails
	except Exception as e:  # The website has different layouts so we adjust accordingly
		print(e)
		expand_button = driver.find_element_by_id("toggle-authors")
		expand_button.click()
		email_text = driver.find_element_by_css_selector("li[data-affiliation-id='affiliation-1']").text
		return email_text
		

def clickNextPage(driver):
	# Finds the button that goes to the next page and clicks it
	next_button = driver.find_element_by_css_selector("span[class='arrow']")
	ActionChains(driver).move_to_element(next_button).click(next_button).perform()

def main():  # Runs the whole program
	search = 'brca1'
	pattern = re.compile(r'[\w\.-]+@[\w\.]+')  # Th pattern that will extract the emails from the page
	# For the Selenium webdriver, the actual scraper
	url = f'https://pubmed.ncbi.nlm.nih.gov/?term={search}&sort=date'  # URL to the specific page
	opts = Options()

	# proxy = "167.99.93.53:8080"  # If you have a working proxy, put it in here(optional)
	# opts.add_argument(f'--proxy-server={proxy}')

	# opts.set_headless()
	# assert opts.headless  # Operating in headless mode. Currently not working
	with webdriver.Chrome(options=opts) as driver:
		driver.get(url)
		search_result = driver.find_element_by_class_name('docsum-title')
		search_result.click()

		with open('emails.csv', 'a', newline='') as csvfile:
			writer_object = csv.writer(csvfile, delimiter=',')
			while True:  # or: for i in range(n): where n is the number of pages you want scraped
				sleep(1)  # To let the CPU rest a bit
				try:
					email_string = findEmail(driver)
					# Extracting the email from the string if there is any string at all
					emails_found = pattern.findall(email_string) if email_string else None
					print('emails found:', emails_found)
					# Cleaning the emails from possible dots at the end
					email_list = list(map(lambda x: x.strip('.'), emails_found)) if emails_found else None
					if email_list:  # If we extracted any emails
						writer_object.writerow(email_list)  # Writing to the csv
				except Exception as e:
					print('Caught Error:', e)
				finally:
					clickNextPage(driver)  # Even if there was an error, move to the next page

main()

