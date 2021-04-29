from django import template
import datetime
import string
import re
register = template.Library()

def to_date(value):
	if value:
		value = str(value)
		data = value.split(' ')
		date = data[0]
		time = data[1]
		time = time.split(':')
		hr = time[0]
		minute = time[1]
		print(hr," ",minute)
		hr = int(hr)
		minute = int(minute)
		print(hr," ",minute)
		hr += 3
		hr = hr % 24
		cracked = date.split('-')
		temp = datetime.datetime(int(cracked[0]), int(cracked[1]), int(cracked[2]),12,0,0)
		if hr>=0 and (hr<3 or (hr==3 and minute==0)):
			temp += datetime.timedelta(days=1)
		hr = str(hr)
		minute = str(minute)
		return str(temp.date())

	return "Not Sent Yet"

def to_str(value):
	return str(value)

def get_year(value):
	string = str(value).strip()
	lst=string.split('-')
	print(lst)
	return int(lst[0])

def get_month(value):
	string = str(value).strip()
	lst=string.split('-')
	print(lst)
	return int(lst[1])

def get_day(value):
	string = str(value).strip()
	lst=string.split('-')
	print(lst)
	return int(lst[2])

def format_cost(value):

	num = str(value)[::-1]
	result = num[0:3]
	i=3
	while i<len(num):
		result=result + "," + num[i:i+3]
		i=i+3
	return result[::-1]


register.filter('to_str',to_str)
register.filter('to_date',to_date)
register.filter('get_day', get_day)
register.filter('get_month',get_month)
register.filter('get_year',get_year)
register.filter('format_cost', format_cost)
