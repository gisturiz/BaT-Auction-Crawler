import re
import json
import csv
import os
import datetime
from requests import get
from bs4 import BeautifulSoup
from pathlib import Path

auction_list = list()

# Call and parse autions page
main_url = 'https://bringatrailer.com/auctions/results/'
response = get(main_url, timeout=5)
soup = BeautifulSoup(response.text, 'html.parser')

def getDate(blurb):
	full_date = blurb.split(' ')[-1]
	# Format date YYYY-MM-DD
	return datetime.date(int('20' + full_date.split('/')[2]), int(full_date.split('/')[0]), int(full_date.split('/')[1]))

def getSoldStatus(blurb):
	if 'Sold' in blurb:
		return True
	return False

def getValue(blurb):
	return blurb.split('$')[1].split(' ')[0].replace(',', '')

def getDateFromCSV(reader):
	lines = []
	for line in reader:
		lines.append(line)
	print(lines[0])
	return None

def checkDateForImport(new_date, csv_date):
	print('checkDateForImport(): Checking data date (' + str(new_date) + ') against CSV file date (' + str(csv_date)) + ')'
	return new_date > csv_date

# TODO: Define functions that will add bid times and amounts to list

def updateCSV(auction_list):
	key_set = set()
	filepath = Path('/home/andrew/Documents/BaT_reports') / 'test_report2.csv'
	file_exists = os.path.isfile(str(filepath))

	for line in auction_list:
		key_set.update(line.keys())
	keys = list(key_set)

	if file_exists:
		print('File exists. Checking dates.')
		with open(str(filepath), 'r') as f:
			csv_lines = f.readlines()
			# Overly complicated date parsing/conversion
			date_string = csv_lines[1].split(',')[0]
			csv_date = datetime.date(int(date_string.split('-')[0]), int(date_string.split('-')[1]), int(date_string.split('-')[2]))
			f.close()
			# If CSV file is already up to date, don't write anything
			if checkDateForImport(auction_list[0]['end_date'], csv_date):
				print('More recent date in new info. Appending file.')
				with open(str(filepath), 'a') as f:
					w = csv.DictWriter(f, keys)
					w.writerows(auction_list)
			else:
				print('File already up to date.')
	else:
		print('File does not exist. Writing.')
		with open(str(filepath), 'w') as f:
			w = csv.DictWriter(f, keys)
			w.writeheader()
			w.writerows(auction_list)

def auctionDataCompiler(title, url, blurb):
	# Example blurb: 'Sold for $92,000 on 2/1/19'
	auction_data = {
		'title': title,
		'url': url,
		'end_date': getDate(blurb),
		'ending_value': getValue(blurb),
		'sold': getSoldStatus(blurb),
		'bid_times': [],
		'bid_amounts': []
	}

	return auction_data

for item in soup.find_all('div', {'class': 'auctions-item-extended'}):
	auction_list.append(auctionDataCompiler(item.find('h3').get_text(), item.find('h3').find('a')['href'], item.find('div').get_text()))

updateCSV(auction_list)
print('Complete')