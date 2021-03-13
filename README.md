# Webstore-Scraper

This program searches **walmart.com** and **target.com** for products that you have inputted. It returns the name, price and image link of the product. Everything is printed on the *stdout*. The input is the product you are searching for( ex. 'Cup').

## Requirements
(Install via pip)

 - bs4
 - requests
 - selenium

# Booking-Scraper

This app scrapes for hotels on **booking.com**, gets all the info about them inside a dictionary then writes it to a json file. The input is any booking hotel link you want.

## Requirements
(Install via pip)

 - bs4
 - requests

# Imdb Scraper

Searches **imdb.com** for movies that the user asked for. It returns the available movie names, ratings, and description.

## Requirements
(Install via pip)

 - bs4
 - requests
 - lxml
 
# Pubmed Scraper

Searches 18,000 pages from *pubmed.ncbi.nlm.nih.gov* for emails. There is no input, and the result emails are sent to a csv file.

## Requirements
(Install via pip)

 - selenium

# SeleniumScrapingTest.py

Scrapes **action.com** specific products for their information. Saves all the data to a dictionary then prints it at the end. Uses mainly *CSS selectors* to extract the data about the product, like the *name, price, ID, Categories, link, image*. The input is the link to the product.


## Requirements
(Install via pip)

 - selenium
 - bs4

### Stable versions for the mentioned libraries
 - bs4(BeautifulSoup) 4.9.3
 - requests 2.25.1
 - selenium 3.141.0
