from requests import get
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json

# Clear contents of file if it exists
open('output.txt', 'w').close()

#Call and parse autions page
main_url = 'https://bringatrailer.com/auctions/results/'
response = get(main_url, timeout=5)
soup = BeautifulSoup(response.text, 'html.parser')
auction_urls = []

#Grab URLs from each auction listed
for link in soup.find_all('h3', {'class': 'auctions-item-title'}):
	link2 = link.find('a')
	if link2.has_attr('href'):
		auction_urls.append(link2['href'])

#Get auction pages and print bid data
def scrapeAuction(url, master_index):
	bidder_names = []
	bid_times = []
	bid_amounts = []

	#Call and parse aution page
	response = get(url, timeout=5)
	soup = BeautifulSoup(response.text, 'html.parser')

	#Get all script tags and set index for the one containing comments & bids
	index = 0
	all_scripts = soup.find_all('script')
	for script in all_scripts:
	    if script.find(text=re.compile('authorLikesFormatted')) and len(script.text) > 1000:
	        break
	    else:
	    	index += 1

	#Isolate JSON from script tag containing comments & bids
	string = all_scripts[index].prettify()
	slice_start = string.find('"address":')
	slice_stop = string.find('};')
	string = '{' + string[slice_start:slice_stop] + '}';
	parsed_comments = json.loads(string)['comments']

	#Iterate through all comments & pull out bids
	for comment in parsed_comments:
		if comment['type'] == 'bat-bid':
			#Get bidder's username
			bidder_name = comment['editableText']
			slice_start = bidder_name.find('/member/') + 8
			slice_stop = bidder_name.find('/" class')
			bidder_name = bidder_name[slice_start:slice_stop]
			bidder_names.append(bidder_name)
			#Get bid's date & time
			bidder_time_str = comment['dateFormatted'].replace(' at', '')
			bidder_time = datetime.strptime(bidder_time_str, '%b %d %I:%M %p').replace(year=2019)
			bid_times.append(str(bidder_time))
			#Get bid amount
			bid_amount = comment['editableText'][1:comment['editableText'].find(' bid placed')].replace(',', '')
			bid_amounts.append(bid_amount)

	#Label winning bidder with '*'
	index = 0
	while index < len(bidder_names):
		if bidder_names[index] == bidder_names[len(bidder_names) - 1]:
			bidder_names[index] += '*'
		index += 1

	#Write tab delimited text file with results
	with open('output.txt', 'a') as f:
		f.write('\t'.join(bidder_names))
		f.write('\n')
		f.write('\t'.join(bid_times))
		f.write('\n')
		f.write('\t'.join(bid_amounts))
		f.write('\n')

	print('Data row ' + str(master_index) + ' of ' + str(len(auction_urls)) + ' (' + str(len(bidder_names)) + ' bids) added to file.')

index = 1
#Call scrapeAuction function for each URL
for url in auction_urls:
	scrapeAuction(url, index)
	index += 1

print('Program complete.')