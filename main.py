from flask import Flask, render_template, request, redirect
from important import *
from handle_post_request import handle_post_request
import json

app = Flask(__name__)


@app.route("/")
def home():
    if ("LOGIN_TOKEN" not in request.cookies or request.cookies["LOGIN_TOKEN"] not in logins):
        return redirect("/login")
    else:
        return redirect("/dashboard")


@app.route("/login")
def login():
    if ("LOGIN_TOKEN" in request.cookies and request.cookies["LOGIN_TOKEN"] in logins):
        return redirect("/dashboard")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    if (request.cookies["LOGIN_TOKEN"] in logins):
        logins.pop(request.cookies["LOGIN_TOKEN"])
    return redirect("/login")


@app.route("/register")
def register():
    if ("LOGIN_TOKEN" in request.cookies and request.cookies["LOGIN_TOKEN"] in logins):
        return redirect("/dashboard")
    else:
        return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if ("LOGIN_TOKEN" not in request.cookies or request.cookies["LOGIN_TOKEN"] not in logins):
        return redirect("/login")
    
    username = logins[request.cookies["LOGIN_TOKEN"]]
    user_data = users.find_one({"username": username})
    created_organizations = []
    joined_organizations = []
    _shifts = []

    for id in user_data["created_organizations"]:
        try:
            name = organizations.find_one({"id": id})["name"]
            created_organizations.append([id, name])
        except:
            pass
    for id in user_data["joined_organizations"]:
        try:
            name = organizations.find_one({"id": id})["name"]
            joined_organizations.append([id, name])
        except:
            pass
    for id in user_data["shifts"]:
        try:
            name = shifts.find_one({"id": id})["name"]
            _shifts.append([id, name])
        except:
            pass

    return render_template("dashboard.html", hours = user_data["hours"], created_organizations = json.dumps(created_organizations), joined_organizations = json.dumps(joined_organizations), shifts = json.dumps(_shifts))   
 

@app.route("/create-organization")
def create_organization():
    if ("LOGIN_TOKEN" not in request.cookies or request.cookies["LOGIN_TOKEN"] not in logins):
        return redirect("/login")
    else:
        return render_template("create_organization.html")
    

@app.route("/organization/<organization_id>")
def organization(organization_id):
    if ("LOGIN_TOKEN" not in request.cookies or request.cookies["LOGIN_TOKEN"] not in logins):
        return redirect("/login")
    
    username = logins[request.cookies["LOGIN_TOKEN"]]
    user_data = users.find_one({"username": username})
    created_organizations = user_data["created_organizations"]

    if (organization_id in created_organizations):
        return redirect(f"/organization/{organization_id}/settings")
    
    organization_data = organizations.find_one({"id": organization_id})
    _shifts = {}

    for shift_id in organization_data["shifts"]:
        shift_data = shifts.find_one({"id": shift_id})
        if (shift_id not in user_data["shifts"] and len(shift_data["volunteers"]) < shift_data["max_holders"]):
            _shifts[shift_id] = {
                "name": shift_data["name"],
                "description": shift_data["description"],
                "available_spots": shift_data["max_holders"] - len(shift_data["volunteers"]),
                "days": shift_data["days"],
                "start_time": shift_data["start_time"],
                "end_time": shift_data["end_time"]
            }
    
    return render_template("organization.html", name = organization_data["name"], description = organization_data["description"], shifts = json.dumps(_shifts))

@app.route("/organization/<organization_id>/settings")
def organization_settings(organization_id):
    if ("LOGIN_TOKEN" not in request.cookies or request.cookies["LOGIN_TOKEN"] not in logins):
        return redirect("/login")
    
    username = logins[request.cookies["LOGIN_TOKEN"]]
    user_data = users.find_one({"username": username})
    created_organizations = user_data["created_organizations"]
    organization_data = organizations.find_one({"id": organization_id})
    _shifts = {}

    for shift_id in organization_data["shifts"]:
        _shifts[shift_id] = shifts.find_one({"id": shift_id})["name"]

    if (organization_data == None or organization_id not in created_organizations):
        return "You do not own any organizations with this ID."
    else:
        return render_template("organization_settings.html", organization_id = organization_id, name = organization_data["name"], description = organization_data["description"], shifts = json.dumps(_shifts), volunteers = json.dumps(organization_data["volunteers"]))


@app.route("/organization/<organization_id>/create-shift")
def create_shift(organization_id):
    if ("LOGIN_TOKEN" not in request.cookies or request.cookies["LOGIN_TOKEN"] not in logins):
        return redirect("/login")
    
    username = logins[request.cookies["LOGIN_TOKEN"]]
    user_data = users.find_one({"username": username})
    created_organizations = user_data["created_organizations"]
    organization_data = organizations.find_one({"id": organization_id})

    if (organization_data == None or organization_id not in created_organizations):
        return "You do not own any organizations with this ID."
    else:
        return render_template("create_shift.html", organization_id = organization_id)
    

@app.route("/shift/<shift_id>/settings")
def view_shift_settings(shift_id):
    if ("LOGIN_TOKEN" not in request.cookies or request.cookies["LOGIN_TOKEN"] not in logins):
        return redirect("/login")
    
    username = logins[request.cookies["LOGIN_TOKEN"]]
    user_data = users.find_one({"username": username})
    created_organizations = user_data["created_organizations"]
    shift_data = shifts.find_one({"id": shift_id})
    organization_id = shift_data["organization"]
    organization_name = organizations.find_one({"id": organization_id})["name"]
    organization_data = organizations.find_one({"id": organization_id})

    if (organization_data == None or organization_id not in created_organizations):
        return "You do not own any organizations with this ID."
    elif (shift_id not in organization_data["shifts"]):
        return "There are no shifts created with this ID."
    else:
        return render_template("shift_settings.html", **shift_data, organization_name = organization_name)
    

@app.route("/shift/<shift_id>")
def view_shift(shift_id):
    pass


@app.route("/browse")
def browse():
    return render_template("browse.html", organization_list = json.dumps(generate_organization_list(request)))


@app.route("/request", methods = {"POST"})
def post_request():
    return handle_post_request(request)


app.run("0.0.0.0")  
