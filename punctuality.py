from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sqlite3
from helpers import dict_factory

# If modifying these scopes, delete the file token.pickle.

def BuildCalendarService():
    # Refer to the Python quickstart on how to setup the environment:
    # https://developers.google.com/calendar/quickstart/python
    # Change the scope to 'https://www.googleapis.com/auth/calendar' and delete any
    # stored credentials.
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    global service
    service = build('calendar', 'v3', credentials=creds)


def AddaNewEvent(EventTitle, EventDate, EventStartTime, EventEndTime, Destination, Description, TimeZone, UserID):   
    BuildCalendarService()
    # make the start time and end time correspond to the RFC3339(ex:2020-11-28T10:00:00) rule
    EventStartTime = EventDate + 'T' + EventStartTime + ':00'
    EventEndTime = EventDate + 'T' + EventEndTime + ':00'
    # save all the info inside event json 
    event = {
                'summary': EventTitle,
                'location': Destination,
                'description': Description,
                'start': {
                    'dateTime': EventStartTime,
                    'timeZone': TimeZone,
                },
                'end': {
                    'dateTime': EventEndTime,
                    'timeZone': TimeZone,
                },
                'recurrence': [
                ],
                'attendees': [
                    
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                    ],
                }
            }

    # add event into database
    conn = sqlite3.connect('punctuality.db', check_same_thread=False)
    conn.row_factory = dict_factory
    c = conn.cursor()
    sql = "INSERT INTO userevents VALUES(?, ?, ?, ?, ?)"
    val = (UserID, EventTitle, EventStartTime, EventEndTime, "Event")
    c.execute(sql, val)
    conn.commit()

    # add event for google calendar
    event = service.events().insert(calendarId='primary', body=event).execute()
    print ('Event created:', (event.get('htmlLink')))


def AddCommuteTime(EventTitle, EventDate, EventStartTime, DepartureLabel, Duration, CommuteTime, CommuteDistance, TimeZone, UserID):
    BuildCalendarService()
    # Calculate commute time (CommuteTime: second) using datetime format
    ArriveAt = EventDate + ' ' + EventStartTime
    ArriveAt = datetime.datetime.strptime(ArriveAt, "%Y-%m-%d %H:%M")
    DepartureFrom = ArriveAt - datetime.timedelta(seconds = CommuteTime)

    
    # make the start time and end time correspond to the RFC3339(ex:2020-11-28T10:00:00) rule
    
    DepartureTime = DepartureFrom.strftime("%Y-%m-%d") + 'T' + DepartureFrom.strftime("%H:%M:%S") 
    print("Departure Time: " + DepartureTime)
    ArrivalTime = EventDate + 'T' + EventStartTime + ':00'
    Summary = ('Departure on: ' + DepartureFrom.strftime("%H:%M:%S") + ', Commute time: '+ Duration )
    Description = ('To: '+ EventTitle + ', From:' + DepartureLabel + ', Distance: ' + CommuteDistance)
    
    event = {
                'summary': Summary,
                'location': [],
                'description': Description,
                'start': {
                    'dateTime': DepartureTime,
                    'timeZone': TimeZone,
                },
                'end': {
                    'dateTime': ArrivalTime,
                    'timeZone': TimeZone,
                },
                'recurrence': [
                ],
                'attendees': [
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                    ],
                }
            }

    
    # add commute into database
    conn = sqlite3.connect('punctuality.db', check_same_thread=False)
    conn.row_factory = dict_factory
    c = conn.cursor()
    sql = "INSERT INTO userevents VALUES(?, ?, ?, ?, ?)"
    val = (UserID, Summary, DepartureTime, ArrivalTime, "Commute")
    c.execute(sql, val)
    conn.commit()

    event = service.events().insert(calendarId='primary', body=event).execute()
    print ('Commute Time created:', (event.get('htmlLink')))
