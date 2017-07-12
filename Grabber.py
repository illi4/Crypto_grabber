## Grabbing crypto announcement dates 
# Saved as grabber.py in the crypto folder

import requests 
import urllib2 
import csv 
from bs4 import BeautifulSoup 
import pprint 
import re 
from datetime import datetime

coins = [] 
coinsdict = {} 
filename = 'coins_all.csv'

check_url = 'https://coinmarketcap.com/currencies/views/all/'
id_search = "currencies-all"

def str_to_numarr(elem): 
    arr = []
    new = re.sub( '\s+', ' ', elem).strip()
    props = new.split(' ')   
    for each in props: 
        each = re.sub("[^0-9]", "", each)
        arr.append(each)
    return arr

with requests.session() as s: 
    
    # Getting all the coins and the urls 
    response = s.get(check_url) 
    response_html = response.text 
    soup = BeautifulSoup(response_html, 'html.parser') 
    
    table = soup.find(id=id_search)

    currencies = table.find_all('td', {'class': 'no-wrap currency-name'})
    for entry in currencies:
        
        # list for properties of currencies
        num_list = []
        
        an_url = ''
        entry_soup = entry.find('img')
        #pprint.pprint(entry_soup)
        curr_name = entry_soup.get('alt')
        #print curr_name
        href_soup=entry_soup.find('a', href=True)
        url = "https://coinmarketcap.com" + href_soup.get('href')
        #print url 
        
        coin_page = s.get(url) 
        coin_html = coin_page.text 
        # Soup for each coin page 
        soup2 = BeautifulSoup(coin_html, 'html.parser') 
        
        # Grabbing announcement dates 
        announcement_search = soup2.find_all('a', href=True)
        for row in announcement_search:
            if "https://bitcointalk.org" in row.get('href'): 
                an_url = row.get('href')
        
        # Grabbing type
        span_s = soup2.find('span', {'class': 'label label-warning'})
        type_s = span_s.text
        if type_s != 'Mineable': 
            type_s = 'Non-minable'
            
        # Grabbing 24h volumes and market cap 
        div_s = soup2.find_all('div', {'class': 'coin-summary-item-detail'})
        for div_detail in div_s: 
            prop = str_to_numarr(div_detail.text)[0]
            num_list.append(prop)

        # Updating dict 
        d = {"coin": curr_name, "url": url, "announcement" : an_url, "minable": type_s, 
             "markcap":num_list[0], "volume24": num_list[1], "date_ann":''} 
        coins.append(d) 
        print(d["coin"])

# Getting actual announcement dates 
for entry in coins: 
    if (entry["announcement"] != '') and (entry["announcement"] != 'https://bitcointalk.org'): 
        #print entry["announcement"]  
        response = s.get(entry["announcement"]) 
        response_html = response.text 
        soup = BeautifulSoup(response_html, 'html.parser')
        posts = soup.find('td', {'class': 'td_headerandpost'})
        if (posts is not None):  
            div_p = posts.find('span', {'class': 'edited'})
            if (div_p is not None):
                datetime_p = datetime.strptime(div_p.text, '%B %d, %Y, %I:%M:%S %p')
                entry["date_ann"] = datetime_p
        
#Done 
#pprint.pprint(coins)
            
# Writing to CSV 
keys = coins[0].keys() 
with open(filename, 'wb') as output_file: 
    dict_writer = csv.DictWriter(output_file, keys) 
    dict_writer.writeheader() 
    dict_writer.writerows(coins) 
        