from flask import make_response
import random, json, pymongo, os
from pymongo import MongoClient


cluster = MongoClient("mongodb+srv://ashwinrramani:0CxvlK09zaIzHzOg@charitycompass.6wgbyhi.mongodb.net/?retryWrites=true&w=majority&appName=CharityCompass")
db = cluster["CharityCompass"]
users = db["users"]
organizations = db["organizations"]
shifts = db["shifts"]


logins = {}

def login_user(username):
	token = generate_login_token()
	logins[token] = username
	resp = make_response("1")
	resp.set_cookie("LOGIN_TOKEN", token)
	return resp


def generate_login_token():
	def inner():
		string = ""
	
		for i in range(20):
			string += random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
	
		return string
	
	string = inner()
	
	while (string in logins):
		string = inner()
	
	return string


def generate_organization_id():
	def inner():
		string = ""

		for i in range(10):
			string += random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
		
		return string
	
	string = inner()

	while (organizations.find_one({"id": string}) != None):
		string = inner()

	return string


def generate_shift_id():
	def inner():
		string = ""

		for i in range(30):
			string += random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
		
		return string
	
	string = inner()

	while (shifts.find_one({"id": string}) != None):
		string = inner()

	return string


# if time1 is greater than time2, the method returns 1
# if time2 is greater than time1, the method returns 2
# if both are equal, the method returns -1
def compare_times(time1, time2):
	hours1, minutes1 = (int(i) for i in time1.split(":"))
	hours2, minutes2 = (int(i) for i in time2.split(":"))
	
	if (hours1 > hours2):
		return 1
	if (hours1 < hours2):
		return 2
	if (minutes1 > minutes2):
		return 1
	if (minutes2 > minutes1):
		return 2
	return -1


def generate_organization_list(request):
	pass
