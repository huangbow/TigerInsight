import sys, csv, collections
import os
from datetime import datetime

class Account:
	
	def __init__(self, array):
		self.account_id = int(array[0])
		self.ap_id = array[1]
		self.device_id = array[2]
		self.timestamp = self.createDateObject(array[3])
		self.arrived = array[4]
		self.completed = array[5]


	def createDateObject(self, str_date, strFormat="%m/%d/%y"): #return the datetime format in specific format
		date = str_date[:str_date.index(' ')]
		timestamp = datetime.strptime(date,strFormat)
		return timestamp

	def FormatDate(self, objectDate,strFormat="%m/%d/%y"): #return string of datetime in specific format
		return objectDate.strftime(strFormat)

def CleanData(file_name, file_to_save_path):
	dict = {}
	# Read data from login.csv, which is renamed & tranformed from SanPedro SoWi Logins - KtH 2016-03-07-3.xlsx
	with open(file_name, 'rb') as csvfile:
		accounts = list(csv.reader(csvfile, delimiter = ','))
		accounts.pop(0)
		for row in accounts:
			if row[0] == "NULL":
				continue
			account = Account(row)

			if isAlreadyThere(account, dict.get(account.account_id)): # for every account, no more than one entry in a day
				continue
			
			dict.setdefault(account.account_id, []).append(account)
 	
 	#clean data
	dict = collections.OrderedDict(sorted(dict.items())); # sort by timestamp

	# Write into .csv file
	file_to_save_path = os.path.join(file_to_save_path, 'login_cleaned.csv')
	with open(file_to_save_path, 'wb') as csvfile:
		accountWriter = csv.writer(csvfile, delimiter = ',')
		#accountWriter.writerow(["Account ID", "Device ID", "timestamp"])
		person_id = 0
		for key in dict:
			dict[key].sort(key=lambda x: x.timestamp, reverse = True) # descending order based on time
			
			if len(dict[key]) < 2: # discard those accounts only have one entry
				continue
			for account in dict[key]:
				accountWriter.writerow([account.account_id, account.FormatDate(account.timestamp), person_id])
			person_id += 1

	return file_to_save_path


def isAlreadyThere(account, accounts_list):
	if accounts_list is None:
		return False
	for element in accounts_list:
		if account.timestamp == element.timestamp:
			return True

	return False


