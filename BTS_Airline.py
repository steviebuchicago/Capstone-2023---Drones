import requests
from bs4 import BeautifulSoup

# Set the URL of the BTS website
url = 'https://www.transtats.bts.gov/Fields.asp?Table_ID=292'

# Send a GET request to the BTS website and get the response
response = requests.get(url, verify=False)

# Parse the HTML response using BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Find the link to download the data
link = soup.find('a', text='Download')

# Set the URL of the data file
data_url = 'https://www.transtats.bts.gov/' + link['href']

# Send a GET request to the data URL and get the response
data_response = requests.get(data_url, verify=False)

# Save the data to a file
with open('airport_data.csv', 'w') as f:
    f.write(data_response.text)
