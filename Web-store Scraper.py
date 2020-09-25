import requests, sys
from bs4 import BeautifulSoup, element
from selenium import webdriver, common
from time import sleep

def search_walmart():
    # Searches the web for the asked product and prints what it finds
    res = requests.get(f'https://www.walmart.com/search/?query={product.lower()}' + ''.join(sys.argv[1:]))
    # Checking for connection
    try: 
      res.raise_for_status()
    except requests.exceptions.HTTPError: 
      print('Connection Error')  # In case the connection fails

    else:  # If there was no error start the process
      soup = BeautifulSoup(res.text, "html.parser")
      print('Walmart.com: \n')

      for i in range(5):  # Getting only the first 5 products from the page
        try:
          outcome_grid = soup.find('li', {'data-tl-id': f'ProductTileGridView-{i}'})  # Finds the grid of the item
          outcome_text = outcome_grid.find('div', {'class': 'search-result-product-title gridview'})  # Then it's text\
          brand_or_name = outcome_text.a.span.get_text(' ', strip=True)  # The brand if it exists, otherwise - name
        except AttributeError:
          print('No such sellable product...\n')
          break
        try:  # Some products don't have a brand and that will raise the error below
          name_after_brand = outcome_text.a.span.next_sibling.get_text(' ', strip=True)
        except AttributeError:
          name_after_brand = None

        try:  # There are some products with no displayed price
          price = outcome_grid.find('span', {'class': 'price-group'}).get_text(strip=True)
        except AttributeError:
          price = 'Price not displayed'
        
        print(brand_or_name)
        if name_after_brand:  # If the brand is displayed
          print(name_after_brand)
        if price:  # If the price is displayed
          print(price)

        # In case the image is not parsed correctly just ignore it (it's useless anyway)
        image_link = outcome_grid.find('img')['src'] if outcome_grid.find('img')['src'].startswith('https') else ''
        print(image_link, '\n')  # Prints the image link


def search_target():
    '''
    This function uses a different approach. As target.com uses an API to display most of the data on the website,
    BeautifulSoup is useless. So, we can make the request directly to the API and it will give us all the data even faster.
    The data is stored as a json file from which the needed products and their price will be extracted.
    '''

    # This is the url to the API (not the website)
    url = f'''https://redsky.target.com/v2/plp/search/?channel=web&count=96&keyword={formatted_product}
              &offset=0&pricing_store_id=3991&key=ff457966e64d5e877fdbad070f276d18ecec4a01'''

    data = requests.get(url).json()  # Gets the data from the API response

    print('Target.com: \n')
    for i in data['search_response']['items']['Item'][:5]:  # Gets the first 5 products
      print('{:<60}\n{}\n{}\n'.format(i['title'], i['price']['formatted_current_price'], 
            i['images'][0]['base_url']+i['images'][0]['primary']))

product = input('What are you searching for?').strip()
formatted_product = '+'.join(product.split(' '))  # The website accepts only splitted words by '+'
search_walmart()
search_target()
