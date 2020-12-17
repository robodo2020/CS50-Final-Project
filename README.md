# PUNCTUALITY

## Welcome to Punctuality
>This is the final project of [CS50x](https://cs50.harvard.edu/x/2020/). It is a web application that helps you add events on your Google Calendar, and automatically tells you the departure time. It simplifies the process of adding a new event and checking the departure time.


## User Instruction
### Register & Login
1. Create a new account by the **"Sign up"** button on the nav-bar, or **"Get Started"** button in hero section. Then click **"Sign in""** to login your account.
![](https://i.imgur.com/nIkX0Hw.png)

### SETTING
Here can setup some default value for you to edit a new event 
1. After login, go to SETTING page to edit your **Address Label* and **Preferences**. 
`(Note: You can use the SCHEDULE function as long as you setup your "Time Zone" and "Commute Mode".  )`
![](https://i.imgur.com/ypJ5y9h.png)


2. Click the <i class="fa fa-edit"></i> button to edit your **Home address** and **Work address**. It will help you to search for the address. 
![](https://i.imgur.com/FZ4oOJ2.png=300x150)
3. Click the **"Add"** and **"Delete"** button to and other address you frequently-used.
![](https://i.imgur.com/dLEXtTu.png=300x150)

4. Click the **Edit** button to setup your Preference **Commute Mode** and **Time Zone**.
`(Note: The Commute Mode will be the default one for adding a new event, you can still select other options if needed.)`

![](https://i.imgur.com/6XYHXts.png=300x160)

### SCHEDULE
This page is for adding new events, getting departure time and commute time. You can also check your calendar and event here.
![](https://i.imgur.com/HLTg7Nu.png)

1. Click the **"New Event"** button
2. Edit the event info such as Title, Date, Time, Destination, and Description.
3. Select the where you will departure. If you will leave from home, just not need to change it.
![](https://i.imgur.com/ALApHbv.png=260x340)

- if you select **"Other"**, you can use other places not in your labels.
    ![](https://i.imgur.com/TrJDUtH.png=200x150)

4. Select the Commute Mode you plan to go to the event. Your preference mode (you set in SETTING page) will be the first choice as well.
![](https://i.imgur.com/sSPZukD.png=200x90)

5. Click the **"Save"** button after you complete.

### Check the event

After schedule you can check your event in calendar. You can click **"month" "week" "day"** to check the event.
![](https://i.imgur.com/EvIjSQD.png)

The calendar will show the event, the commute time you need, and when to departure.

You can also find the same event,commute time and departure time on your goolge calendar.  
![](https://i.imgur.com/sbJWrzh.png)

## Project Description
### Frameworks/Libraries
Below are the resources I used to build this project.
- [Flask](https://flask.palletsprojects.com/en/1.1.x/)
- [SQLite](https://www.sqlite.org/index.html)
- Google Cloud Platform
    - [Distance Matrix API](https://developers.google.com/maps/documentation/distance-matrix/overview)
    - [Places API](https://developers.google.com/places/web-service/overview)
    - [Calendar API](https://developers.google.com/calendar)
- [Jinja2](https://jinja.palletsprojects.com/en/2.11.x/)
- [Bootstrap](https://getbootstrap.com/)
- [BootstrapMade](https://bootstrapmade.com/)
- [DatePicker](https://fengyuanchen.github.io/datepicker/)
- [TimePicker](https://www.jonthornton.com/jquery-timepicker/)
- [FullCalendar](https://fullcalendar.io/)




