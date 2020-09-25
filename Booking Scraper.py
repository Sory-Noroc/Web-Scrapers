# Script that scrapes for hotels on booking.com, gets all the info about them and writes to a json file. The input is a booking hotel link.

from json import dump
import requests
from bs4 import BeautifulSoup


class Hotel:
	def __init__(self, link):
		'''
		.strip('\n') and .replace('\n', '') will be used a lot to get rid of '\n's in the data and make it look good
		'''
		self.link = link  # To work with the json later
		res = requests.get(link)  # accessing the website source code
		soup = BeautifulSoup(res.text, 'html.parser')  # parsing the source html
		self.hotel_dict = {  # The dictionary with all the info
		'url' : link
		}
		hotel_name_type = soup.find('h2', id='hp_hotel_name')  # Extracting the hotel name/type
		self.hotel_dict['name'] = hotel_name_type.contents[2].strip('\n')  # Getting the correct hotel name
		self.hotel_dict['hotelType'] = hotel_name_type.span.text.strip('\n')  # Then type
		self.hotel_dict['ratingOverall'] = soup.find('div', class_='bui-review-score__badge').get_text(strip=True)
		# Lower we will extract (only) the star rating from the whole string with the text that says '4 star rating'
		self.hotel_dict['numberOfStars'] = [
		# There we extract the number of stars from the string looking like so '4 star rating'
		char for char in soup.find('i', class_=" bk-icon-wrapper bk-icon-stars star_track ")['title'] if char.isdigit()
		][0]

		for rating_tag in soup.find_all('div', class_='c-score-bar'):  # Looping through ratings (they got the same class)
		# Here, instead of typing each rating variable, we will use only the following line for all of them
			self.hotel_dict[rating_tag.span.text.replace(' ', '') + 'Rating'] = rating_tag.find('span', class_='c-score-bar__score').text

		self.hotel_dict['adress'] = soup.find('span', class_=" hp_address_subtitle js-hp_address_subtitle jq_tooltip ").text.strip('\n')
		self.hotel_dict['description'] = soup.find('div', id='property_description_content').text.replace('\n', '')
		facilities = {}
		for facility in soup.find_all('div', class_='facilitiesChecklistSection'):  # Finding all facilities
			facility_dict = {}  # Temporary dictionary to add what is scraped
			facil = facility.find('h5').contents[2].strip('\n')  # facility name
			facility_dict[facil] = []  # Temporary list that will hold the facility elements
			for tag in facility.find_all('li'):
				string = ''
				for string_ in tag.strings:
					string += string_
				facility_dict[facil].append(string.strip('\n').replace('\n', ' '))  # Cleaning the strings of \n

			facilities.update(facility_dict)  # Adding the new facility

		self.hotel_dict['Facilities'] = facilities  # Adding the facilities to our main dictionary

	def dict_to_json(self):
		with open(f"{self.link.split('/')[-1].split('html')[0]}.json", 'w') as json_file:  # This mess is to choose a normal file name
			dump(self.hotel_dict, json_file, ensure_ascii=False, indent=4)  # writing to the file


# Below is the link to be inserted for data extracting

booking_link = input('Paste link: ')
scraped_hotel = Hotel(booking_link)
scraped_hotel.dict_to_json()  # Voila
