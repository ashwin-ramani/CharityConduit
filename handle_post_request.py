import json
from important import *


def handle_post_request(request):
	request_data = json.loads(request.data)

	for field in request_data:
		if (request_data[field] == ""):
			return "99"
		

	if (request_data["purpose"] == "login"):
		username = request_data["username"].strip().lower()
		password = request_data["password"]

		if (users.find_one({"username": username}) == None):
			return "0"
		if (password != users.find_one({"username": username})["password"]):
			return "0"

		return login_user(username)


	elif (request_data["purpose"] == "register"):
		first_name = request_data["first_name"].strip().capitalize()
		last_name = request_data["last_name"].strip().capitalize()
		username = request_data["username"].strip().lower()
		password = request_data["password"]

		if (users.find_one({"username": username}) != None):
			return "0"

		users.insert_one({
			"first_name": first_name,
			"last_name": last_name,
			"username": username,
			"password": password,
			"hours": 0,
			"created_organizations": [],
			"joined_organizations": [],
			"shifts": []
		})

		return login_user(username)
	

	elif (request_data["purpose"] == "create_organization"):
		if ("LOGIN_TOKEN" not in request.cookies or request.cookies["LOGIN_TOKEN"] not in logins):
			return "0"
	
		name = request_data["name"].strip()
		description = request_data["description"].strip()
		id = generate_organization_id()
		city = request_data["city"].strip()
		state = request_data["state"].strip()
		organizations.insert_one({
			"name": name,
			"description": description,
			"id": id,
			"city": city,
			"state": state,
			"shifts": [],
			"volunteers": {}
		})

		username = logins[request.cookies["LOGIN_TOKEN"]]
		users.update_one({"username": username}, {"$push": {"created_organizations": id}})

		return id
	

	elif (request_data["purpose"] == "edit_organization_data"):
		if ("LOGIN_TOKEN" not in request.cookies or request.cookies["LOGIN_TOKEN"] not in logins):
			return "0"
		
		organization_id = request_data["organization_id"]
		username = logins[request.cookies["LOGIN_TOKEN"]]

		if (organization_id not in users.find_one({"username": username})["created_organizations"]):
			return "1"
		
		name = request_data["name"].strip()
		description = request_data["description"].strip()
		organizations.update_one({"id": organization_id}, {"$set": {
			"name": name, 
			"description": description
		}})

		return "2"
	

	elif (request_data["purpose"] == "delete_organization"):
		if ("LOGIN_TOKEN" not in request.cookies or request.cookies["LOGIN_TOKEN"] not in logins):
			return "0"
		
		organization_id = request_data["organization_id"]
		username = logins[request.cookies["LOGIN_TOKEN"]]

		if (organization_id not in users.find_one({"username": username})["created_organizations"]):
			return "1"
		
		organizations.delete_one({"id": organization_id})
		shifts.delete_many({"organization": organization_id})
		users.update_one({"username": username}, {"$pull": {"created_organizations": organization_id}})

		return "2"
		

	elif (request_data["purpose"] == "create_shift"):
		if ("LOGIN_TOKEN" not in request.cookies or request.cookies["LOGIN_TOKEN"] not in logins):
			return "0"
		
		organization_id = request_data["organization_id"]
		username = logins[request.cookies["LOGIN_TOKEN"]]

		if (organization_id not in users.find_one({"username": username})["created_organizations"]):
			return "You do not own this organization."
	
		name = request_data["name"].strip()
		description = request_data["description"].strip()
		start_time = request_data["start_time"]
		end_time = request_data["end_time"]
		max_holders = int(request_data["max_holders"])
		days = request_data["days"]
		shift_id = generate_shift_id()

		if (max_holders < 1):
			return "-2"
		if (compare_times(end_time, start_time) != 1):
			return "-1"

		for time in (start_time, end_time):
			hours, minutes = (int(i.strip()) for i in time.split(":"))
			assert hours <= 25 and hours >= 0
			assert minutes <= 59 and minutes >= 0

		organizations.update_one({"id": organization_id}, {"$push": {"shifts": shift_id}})
		shifts.insert_one({
			"id": shift_id,
			"organization": organization_id,
			"name": name,
			"description": description,
			"start_time": start_time,
			"end_time": end_time,
			"days": days,
			"max_holders": max_holders,
			"volunteers": {}
		})

		return shift_id
	
	
	elif (request_data["purpose"] == "edit_shift_data"):
		if ("LOGIN_TOKEN" not in request.cookies or request.cookies["LOGIN_TOKEN"] not in logins):
			return "0"
		
		organization_id = request_data["organization_id"]
		username = logins[request.cookies["LOGIN_TOKEN"]]

		if (organization_id not in users.find_one({"username": username})["created_organizations"]):
			return "1"
		
		shift_id = request_data["id"]
		name = request_data["name"].strip()
		description = request_data["description"].strip()
		start_time = request_data["start_time"]
		end_time = request_data["end_time"]
		max_holders = int(request_data["max_holders"])

		if (max_holders < 1):
			return "-2"
		if (compare_times(end_time, start_time) != 1):
			return "-1"
		
		shifts.update_one({"id": shift_id}, {"$set": {
			"name": name, 
			"description": description, 
			"start_time": start_time, 
			"end_time": end_time, 
			"max_holders": max_holders
		}})

		return "2"
	

	elif (request_data["purpose"] == "delete_shift"):
		if ("LOGIN_TOKEN" not in request.cookies or request.cookies["LOGIN_TOKEN"] not in logins):
			return "0"
		
		organization_id = request_data["organization_id"]
		username = logins[request.cookies["LOGIN_TOKEN"]]

		if (organization_id not in users.find_one({"username": username})["created_organizations"]):
			return "1"
		
		shift_id = request_data["id"]
		shifts.delete_one({"id": shift_id})
		organizations.update_one({"id": organization_id}, {"$pull": {"shifts": shift_id}})

		return "2"
		
	
	if (request_data["purpose"] == "take_shift"):
		if ("LOGIN_TOKEN" not in request.cookies or request.cookies["LOGIN_TOKEN"] not in logins):
			return "0"
		
		organization_id = request_data["organization_id"]
		shift_id = request_data["shift_id"]
		username = logins[request.cookies["LOGIN_TOKEN"]]
		user_data = users.find_one({"username": username})
		organization_data = organizations.find_one({"id": organization_id})
		shift_data = shifts.find_one({"id": shift_id})

		if (len(shift_data["volunteers"]) == shift_data["max_holders"]):
			return "0"

		if (organization_id not in user_data["created_organizations"] and organization_id not in user_data["joined_organizations"]):
			users.update_one({"username": username}, {"$push": {"joined_organizations": organization_id}})
		
		users.update_one({"username": username}, {"$push": {"shifts": shift_id}})
		shifts.update_one({"id": shift_id}, {"$set": {f"volunteers.{username}": 0}})

		if (username not in organization_data["volunteers"]):
			organizations.update_one({"id": organization_id}, {"$set", {f"volunteers.{username}": {
				"shifts": [shift_id],
				"hours": 0
			}}})
		else:
			organizations.update_one({"id": organization_id}, {"$push": {f"volunteers.{username}.shifts": shift_id}})

		return "1"
