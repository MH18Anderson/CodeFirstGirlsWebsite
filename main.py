import sqlite3
import os
from sqlite3 import Error
from flask import (Flask, request, render_template, session,
                   g, redirect, url_for, abort, flash)
import requests

# Connects to a database using sqlite3


def connect_db(database_file):
    conn = sqlite3.connect(database_file)
    return conn


# Selects all events relating to a specific user
def select_all(conn, user):
    cursor = conn.cursor()
    sql = ('SELECT * FROM CALENDAR_%s' % (user))
    cursor.execute(sql)

    rows = cursor.fetchall()
    return rows


# Inserts an event into the user's calender. Note that params is a list that must contain (ID, start_time, end_time, day, event_name, event_location)
def insert(conn, user, params):
    cursor = conn.cursor()
    sql = ('INSERT INTO CALENDAR_%s VALUES(?,?,?,?,?,?)' % (user))
    cursor.execute(sql, params)
    conn.commit()

# If the user does not have a table, create one!


def createtable(conn, user):
    cursor = conn.cursor()
    sql = ('CREATE TABLE if not exists CALENDAR_%s (d0 TEXT PRIMARY KEY, d1 TEXT, d2 TEXT, d3 TEXT, d4 TEXT, d5 TEXT)' % (user))
    cursor.execute(sql)
    conn.commit()

# Since every entry in a databse needs a unique key, a very messy one is created by just creating a massive string of the properties of the event
# so if the user is "oliwia" and the event has start time at 10, end at 11, has the name "lecture" and is in "founders", then the key would
# be ID = oliwia1011lecturefounders


def generate_ID(user, params):
    for p in params:
        user = user + p
    return user


'''
This creates a big empty table with 7 columns (to represent the days) and 15 rows (to represent the times)
This algorithm does the following:
1. Get all events that a user has
2. Nested for loop that goes over all events and all hours, from 6 to 20.
3. When looping through the times, if the current time is in between the start and end time, then fill in the table cell with the name of the event and its location
'''


def event(conn, user):
    #represents a big empty calendar
    event_table = [["" for x in range(0, 7)] for y in range(0, 15)]
    #get all of a user's events
    available_events = select_all(conn, user)

    #for each event
    for a in available_events:
        #go over all possible times the event could take place, ie from 6 to 8
        for i in range(6, 21):
            #if i (which represents the time we currently looking at) is greater or equal to the start time of the event, or less than or equal to the end time of the event, fill it up with the event's details
            if i >= int(a[1]) and i <= int(a[2]):
                print(i, int(a[1]), int(a[2]))
                event_table[i-6][int(a[3])
                                 ] = "Event: {} in: {}".format(a[4], a[5])
    return event_table


app = Flask(__name__)

#The Flask documentation recommends using a database by starting off the program as such. This will just set up some variables for Flask to use in the future
app.config.from_object(__name__)
app.config.update(
    #which database file are we going to use
    DATABASE=os.path.join(app.root_path, 'calendar.db'),
    #we don't know the name of the user yet so just set it to blank
    NAME=""
)


@app.route('/')
def main_page():
    return render_template('index.html')

#Returns the dashboard - the event_table is created to wipe out the previous calendar in case it contained information about another user's schedule
#It then renders a HTML file along with the events that occur at each hour so the calendar will fill up
@app.route("/dashboard", methods=["GET"])
def sign_up():
    event_table = [["" for x in range(0, 7)] for y in range(0, 15)]
    #connect to database and if user has not used the services, return a blank calendar. Else, it will return the user's calendar, which will be stored in event_table
    conn = connect_db(app.config['DATABASE'])
    createtable(conn, app.config['NAME'])
    event_table = event(conn, app.config['NAME'])
    conn.close()
    #this return is explained above
    return render_template('dashboard.html', six=event_table[0], seven=event_table[1], eight=event_table[2], nine=event_table[3], ten=event_table[4], eleven=event_table[5], twelve=event_table[6], thirteen=event_table[7], fourteen=event_table[8], fifteen=event_table[9], sixteen=event_table[10], seventeen=event_table[11], eighteen=event_table[12], nineteen=event_table[13], twenty=event_table[14], user=app.config['NAME'])

#Uses mailgun to welcome the user
def send_simple_message(address):
    return requests.post(
        "https://api.mailgun.net/v3/sandboxb298abe6bf9b4f2597ff936c91181223.mailgun.org/messages",
        auth=("api", "dc8d31d20b0995dd1e58bfc3dc650cd6-de7062c6-b92fa5a7"),
        data={"from": "University of Bath Dashboard <mailgun@sandboxb298abe6bf9b4f2597ff936c91181223.mailgun.org>",
              "to": [address],
              "subject": "University made easier ;)",
              "text": "Thanks for signing up!"})



@app.route("/dashboard", methods=["POST"])
def calendar_post():
    #If the user came from the welcome page
    if "email" in request.form:
        #get the user's details and update the username in the application's configuration
        email = request.form["email"]
        app.config.update(
            DATABASE=os.path.join(app.root_path, 'calendar.db'),
            NAME=request.form["username"]
        )
        course = request.form["course"]
        #send an email
        send_simple_message(email)

        #connect to the database and retrieve their calendar if they have already used the service or return an empty one
        conn = connect_db(app.config['DATABASE'])
        createtable(conn, app.config['NAME'])
        event_table = event(conn, app.config['NAME'])
        conn.close()
        #go to dashboard.html - the explanation for all the extra items can be found in previous comments
        return render_template('dashboard.html', six=event_table[0], seven=event_table[1], eight=event_table[2], nine=event_table[3], ten=event_table[4], eleven=event_table[5], twelve=event_table[6], thirteen=event_table[7], fourteen=event_table[8], fifteen=event_table[9], sixteen=event_table[10], seventeen=event_table[11], eighteen=event_table[12], nineteen=event_table[13], twenty=event_table[14], user=app.config['NAME'])
    #if the user added an event 
    else:
        #get event details such as days
        day = request.form['days']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        event_name = request.form['event_name']
        event_local = request.form['event_local']
        #generate the silly ID
        id = generate_ID(
            app.config['NAME'], (day, start_time, end_time, event_name, event_local))
        #connect to the database and insert the event
        conn = connect_db(app.config['DATABASE'])
        insert(conn, app.config['NAME'], (id, start_time,
                                          end_time, day, event_name, event_local))
        #get the calendar again so it updates
        event_table = event(conn, app.config['NAME'])
        conn.close()
        #go to dashboard.html - the explanation for all the extra items can be found in previous comments
        return render_template('dashboard.html', six=event_table[0], seven=event_table[1], eight=event_table[2], nine=event_table[3], ten=event_table[4], eleven=event_table[5], twelve=event_table[6], thirteen=event_table[7], fourteen=event_table[8], fifteen=event_table[9], sixteen=event_table[10], seventeen=event_table[11], eighteen=event_table[12], nineteen=event_table[13], twenty=event_table[14], user=app.config['NAME'])

      
      
# will request the news articles 'Powered by NewsApi'
@app.route('/', methods=['GET'])
@cross_origin()
def find_news():
    newsapi = NewsApiClient(api_key='becec0b66fa741fb9868408992b4587a')


    # get all articles relating to users' course
    all_articles = newsapi.get_everything(q=str(course),
                                         sources='bbc-news, bloomberg, business-insider-uk, financial-times',
                                         domains='bbc.co.uk, bloomberg.com, uk.businessinsider.com, ft.com',
                                         from_param='2019-03-01',
                                         to='2019-03-20',
                                         language='en',
                                         sort_by='relevancy',
                                         page=2)

    #results = []

    #for ar in all_articles:
    #    results.append(ar)

    #for i in range(len(results)):
        # printing all trending news
    #    print(i + 1, results[i])

    return jsonify(all_articles)      
      
#run the app
app.run()

import requests
endpoint = "http://api.openweathermap.org/data/2.5/weather"
payload = {"q": "Bath,UK", "units":"metric", "appid":"3227536aa5b26a0669b46b00f13dfb11"}
response = requests.get(endpoint, params=payload)
data = response.json()

print data["main"]
print response.url
print response.status_code
print response.headers["content-type"]
print response.text

temperature = data["main"]["temp"]
name = data["name"]
weather = data["weather"][0]["main"]
print u"It's {}C in {}, and the sky is {}".format(temperature, name, weather)


'''
Issues:
1. It will always send an email welcoming the user, whether they have signed up before or not
2. No password
3. No verification if the details are actually correct
4. Calendar may look a bit ugly and lacks features such as deleting and updating or even spanning multiple weeks
5. News feature is not fully integrated
'''
