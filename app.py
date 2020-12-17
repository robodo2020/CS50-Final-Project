import os
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, dict_factory

import sqlite3
import googlemaps
from punctuality import AddaNewEvent, AddCommuteTime
import datetime
from dotenv import load_dotenv
load_dotenv()

# Configure application 
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True




# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

AllCommuteMode =['driving','transit','bicycling','walking']

# Register & Login
@app.route("/", methods=["POST"])
def register_login():
# Register
    if request.form.get("RegUsername"):
        """Register user"""
        # Forget any user_id
        session.clear()
        RegUsername = request.form.get("RegUsername")
        RegPassword = request.form.get("RegPassword")
        RegConfirmPassword = request.form.get("RegConfrimPassword")

        if RegPassword == RegConfirmPassword:
            HashPassword = generate_password_hash(RegPassword)
            with sqlite3.connect('punctuality.db') as conn:
                c = conn.cursor()
                sql = "INSERT INTO userinfo (username, pwhash) VALUES (?, ?)"
                val = (RegUsername ,HashPassword)
                c.execute(sql, val)
                conn.commit()
            return redirect("/")
        else:
            return apology("Passwords don't match", 403)
# Login
    elif request.form.get("LoginUsername"):
        """Log user in"""
        # Forget any user_id
        session.clear()

        LoginUsername = request.form.get("LoginUsername")
        LoginPassword = request.form.get("LoginPassword")   
        # Ensure username was submitted
        if not LoginUsername: 
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not LoginPassword:
            return apology("must provide password", 400)

        # Query database for username
        with sqlite3.connect('punctuality.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM userinfo WHERE username = ?", (LoginUsername,))
            rows = c.fetchone()
            conn.commit()
        if rows == None:
            return apology("No this user", 403)
        if not check_password_hash(rows[2], LoginPassword):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]

        # Redirect user to home page
        return redirect("/schedule")

    
# index
@app.route("/")
# @login_required
def index():
    return render_template("index.html")



# Schedule
@app.route("/schedule", methods=["GET","POST"])
@login_required
def schedule():
    conn = sqlite3.connect('punctuality.db', check_same_thread=False)
    conn.row_factory =dict_factory
    c = conn.cursor()

    # get home address data from database, and save it inside home
    c.execute("SELECT * FROM useraddress WHERE uid=? and label=?", (session["user_id"],"Home",))
    home = c.fetchone()
    c.execute("SELECT * FROM useraddress WHERE uid=? AND label=?", (session["user_id"],"Work",))
    work = c.fetchone()
    c.execute("SELECT address, label FROM useraddress WHERE uid=? AND label<>? AND label<>? ", (session["user_id"],"Work","Home"))
    CustomList = c.fetchall()
    print(CustomList)

    # get already saved commute events and commute 
    c.execute("SELECT * FROM userevents WHERE uid=?", (session["user_id"],))
    UserEvents = c.fetchall()


    # get user commute mode and from database, and save it
    c.execute("SELECT commutemode FROM userpreferences WHERE uid=?",(session["user_id"],))
    UserCommuteMode = c.fetchone()
    if UserCommuteMode:
        UserCommuteMode = UserCommuteMode['commutemode'].capitalize()
    

    # get user timezone and from database, and save it 
    c.execute("SELECT timezone FROM userpreferences WHERE uid=?",(session["user_id"],))
    TimeZone = c.fetchone()
    if TimeZone:
        TimeZone = TimeZone['timezone']  
    else:
        TimeZone = None


    if request.method == "GET":
        api_key = os.environ.get("API_KEY")
        return render_template("schedule.html", CustomList= CustomList, AllCommuteMode = AllCommuteMode, UserCommuteMode = UserCommuteMode, UserEvents= UserEvents, home = home, work = work, TimeZone = TimeZone, API_KEY = api_key)
    else:
    # Get the event information from user input
        EventTitle = request.form.get("EventTitle")
        EventDate = request.form.get("EventDate")
        EventStartTime = request.form.get("EventStartTime")
        EventEndTime = request.form.get("EventEndTime")
        Destination = request.form.get("Destination")
        DepartureLabel = request.form.get("DepartureLabel")  # return only label
        DepartureUserInput = request.form.get("DepartureUserInput") # return address
        Description = request.form.get("Description")
        CalculateCommuteMode = (request.form.get("CalculateCommuteMode")).lower() # switch to lowercase since the demends for distance matrix api
        
        # Mix Mode: Function hasn't complete
        # # mix mode
        # if CalculateCommuteMode =='Mix':
        #     FirstWaypoint = request.form.get("FirstWaypoint")
        #     FirstWaypointMode = request.form.get("FirstWaypointMode")
        #     SecondWaypoint = request.form.get("SecondWaypoint")
        #     SecondWaypointMode = request.form.get("SecondWaypointMode")

        # error handling for the must required variables 
        if EventTitle=="" or EventDate =="" or EventStartTime == "" or EventEndTime =="" or Destination=="" or DepartureLabel == "":
            return  apology("Please fill in all the informaiton", 400)

        if DepartureLabel == 'Other' and DepartureUserInput:   
            DepartureAddress = DepartureUserInput
            DepartureLabel = DepartureUserInput
        # error handling for user didn't input Departure place
        elif DepartureLabel == 'Other'and DepartureUserInput =="":
            return  apology("Please input Departure place", 400)

        # Get the address from label
        else:
            c.execute("SELECT address FROM useraddress WHERE uid=? and label=?", (session["user_id"],DepartureLabel))
            DepartureAddress = c.fetchone()
            DepartureAddress = DepartureAddress['address']
        
        # Change the type of EventStartTime to datetime.datetime
        EventStartDateTime = EventDate + ' ' + EventStartTime
        EventStartDateTime = datetime.datetime.strptime(EventStartDateTime, "%Y-%m-%d %H:%M")

        
        # Calculate the distance and time for commute
        api_key = os.environ.get("API_KEY")
        gmaps = googlemaps.Client(key=api_key)
        place = gmaps.distance_matrix(DepartureAddress, Destination,CalculateCommuteMode,None,None,None,None,EventStartDateTime,None,None,None,None)
        print(place)

        if place['rows'][0]['elements'][0] == {'status': 'ZERO_RESULTS'}:
            return apology("Cannot estimate the time", 403)


        # Add event on google calendar
        AddaNewEvent(EventTitle, EventDate, EventStartTime, EventEndTime, Destination, Description, TimeZone, session["user_id"])
    
        # Calculate commute time on google calendar
        CommuteDistance = place['rows'][0]['elements'][0]['distance']['text']
        CommuteTime = place['rows'][0]['elements'][0]['duration']['value'] #return seconds
        Duration = place['rows'][0]['elements'][0]['duration']['text']
        AddCommuteTime(EventTitle, EventDate, EventStartTime, DepartureLabel, Duration, CommuteTime, CommuteDistance, TimeZone, session["user_id"])
        return redirect("/schedule")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")



@app.route("/settings",  methods=["GET","POST"])
@login_required
def settings():
    conn = sqlite3.connect('punctuality.db', check_same_thread=False)
    conn.row_factory =dict_factory
    c = conn.cursor()

    # get home address data from database, and save it inside home
    c.execute("SELECT * FROM useraddress WHERE uid=? and label=?", (session["user_id"],"Home",))
    home = c.fetchone()

    # get work address data from database, and save it inside home
    c.execute("SELECT * FROM useraddress WHERE uid=? AND label=?", (session["user_id"],"Work",))
    work = c.fetchone()

    c.execute("SELECT address, label FROM useraddress WHERE uid=? AND label<>? AND label<>? ", (session["user_id"],"Work","Home"))
    CustomList = c.fetchall()

    # get user commute mode and from database, and save it inside 
    c.execute("SELECT commutemode FROM userpreferences WHERE uid=?",(session["user_id"],))
    CommuteMode = c.fetchone()
    
    # get user timezone and from database, and save it inside 
    c.execute("SELECT timezone FROM userpreferences WHERE uid=?",(session["user_id"],))
    TimeZone = c.fetchone()



    # get timezone data
    c.execute("SELECT timezone FROM zone ORDER BY timezone ASC")
    AllTimeZoneData = c.fetchall()

    # Web GET POST method check
    if request.method == "GET":
        # check if user has set the home address, and return to web
        if home:
            HomeAddress = home['address']
        else:
            HomeAddress = None

        # check if user has set the work address, and return to web
        if work:
            WorkAddress = work['address']
        else:
            WorkAddress = None
        
        # check if user has set the commute mode, and return to web
        if CommuteMode:
            UserCommuteMode = CommuteMode['commutemode'].capitalize()
            # AllCommuteMode =SortCommuteMode(UserCommuteMode)
        else:
            UserCommuteMode = None

        # check if user has set the timezone, and return to web
        if TimeZone:
            UserTimeZone = TimeZone['timezone']
        else:
            UserTimeZone = None
        api_key = os.environ.get("API_KEY")
        return render_template("settings.html",HomeAddress = HomeAddress, WorkAddress = WorkAddress, CustomList = CustomList, AllTimeZoneData = AllTimeZoneData, UserCommuteMode = UserCommuteMode, UserTimeZone = UserTimeZone, AllCommuteMode = AllCommuteMode,API_KEY = api_key)


    else:
        # get the work/address data from edit address request
        InputHomeAddress = request.form.get("InputHomeAddress")
        InputWorkAddress = request.form.get("InputWorkAddress")

        # add custom address function
        InputCustomLabel = request.form.get("InputCustomLabel")
        InputCustomAddress = request.form.get("InputCustomAddress")
        DeleteLabel = request.form.get("DeleteLabel")

        # get the user commute mode/timezone from edit request
        InputCommuteMode = (request.form.get("InputCommuteMode"))
        InputTimeZone = request.form.get("InputTimeZone")
        

        # if home address has already setup, then edit and update. Else, insert into database
        if InputHomeAddress:
            if home:
                sql = "UPDATE useraddress SET address = ? WHERE uid=? AND label=?"
                val = ( InputHomeAddress, session["user_id"], "Home")
                c.execute(sql, val)
                conn.commit()
            else:
                sql = "INSERT INTO useraddress VALUES(?, ?, ?)"
                val = (session["user_id"], InputHomeAddress, "Home")
                c.execute(sql, val)
                conn.commit()
        
        # if work address has already setup, then edit and update. Else, insert into database
        if InputWorkAddress:
            if work:
                sql = "UPDATE useraddress SET address =? WHERE uid=? AND label=?"
                val = (InputWorkAddress, session["user_id"], "Work")
                c.execute(sql, val)
                conn.commit()
            else:
                sql = "INSERT INTO useraddress VALUES(?, ?, ?)"
                val = (session["user_id"], InputWorkAddress, "Work")
                c.execute(sql, val)
                conn.commit()

        # save custom address to database
        if InputCustomLabel and InputCustomAddress:
            sql = "INSERT INTO useraddress VALUES(?, ?, ?)"
            val = (session["user_id"], InputCustomAddress, InputCustomLabel)
            c.execute(sql, val)
            conn.commit()
        # error handling
        elif InputCustomLabel == "" or InputCustomAddress == "":
            return apology("Please fill in the New label form", 400)


        # delete custom address
        if DeleteLabel:
            sql = "DELETE FROM useraddress WHERE uid=? AND label=?"
            val = (session["user_id"],DeleteLabel)
            c.execute(sql, val)
            conn.commit()

       
        # if custom commute mode and timezone has already setup,then edit and update. Else, insert into database
        if InputCommuteMode and InputTimeZone:
            InputCommuteMode = InputCommuteMode.lower() # switch to lowercase since the demends for distance matrix api
            if CommuteMode and TimeZone:
                sql = "UPDATE userpreferences SET timezone=?, commutemode=? WHERE uid=?"

                val = (InputTimeZone, InputCommuteMode, session["user_id"])
                c.execute(sql, val)
                conn.commit()
            else:
                sql = "INSERT INTO userpreferences VALUES(?, ?, ?)"
                val = (session["user_id"], InputTimeZone, InputCommuteMode)
                c.execute(sql, val)
                conn.commit()
        elif InputCommuteMode and InputTimeZone == None:
                return apology("Please select your Time Zone", 400)
        elif InputCommuteMode == None and InputTimeZone:
                return apology("Please select your Commute Mode", 400)

        return redirect("/settings")


# Change Password page
@app.route("/changepw", methods = ["GET","POST"])
@login_required
def changepw():
    conn = sqlite3.connect('punctuality.db', check_same_thread=False)
    conn.row_factory =dict_factory
    c = conn.cursor()

    if request.method =="GET":
        return render_template("changepw.html")
    else:
        originalpw = request.form.get("originalpw")
        newpw = request.form.get("newpw")
        newpwagain = request.form.get("newpwagain")

        # check original password match
        c.execute("SELECT pwhash FROM userinfo WHERE id =?", (session["user_id"],))
        UserHashPassword = c.fetchone()
        if not check_password_hash(UserHashPassword['pwhash'], originalpw):
            return apology("Wrong Original Password", 403)

        if newpw == newpwagain:
            hashpassword = generate_password_hash(newpw)
            sql = "UPDATE userinfo SET pwhash=? WHERE id=?"
            val = (hashpassword ,session["user_id"])
            c.execute(sql, val)
            conn.commit()
            return redirect("/schedule")
        else:
            return apology("New Passwords don't match", 403)
        return redirect("/")