__author__ = 'mthepyromaniac'


import twilio.rest
from twilio.rest import TwilioRestClient
import twilio.twiml
from flask import Flask
from flask import render_template
import os
import praw
from flask import request
import re
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

api = Flask(__name__)

headline = "something"
userAgent = praw.Reddit(user_agent='headline_call v1.0')
result = "Click here to schedule a call!"
account_sid = "sid"
auth_token = "token"
client = TwilioRestClient(account_sid, auth_token)
toNumber = "number"
fromNumber = "number"
minute = 59
day = "sun"
hour = 13

#Functions:
def RedditHeadline():
    submissions = userAgent.get_front_page(limit=1)
    for item in submissions:
        return item

def MakeCall():
    headline = str(RedditHeadline())
    headline = headline[7:]
    headline = headline.replace(" ","%20") #transform headline to proper format
    try:
        call = client.calls.create(to=toNumber,
                           from_=fromNumber,
                           url= "http://twimlets.com/echo?Twiml=%3C%3Fxml%20version%3D%221.0%22%20encoding%3D%22UTF-8%22%3F%3E%3CResponse%3E%3CSay%20voice%3D%22alice%22%3EHello.%20Michelle%20Rooy.%20The%20top%20reddit%20headline%20for%20today%20is%20%7B%7B%20"+ headline + "%20%7D%7D%20%3C%2FSay%3E%3C%2FResponse%3E&")
        print(headline)
    except twilio.rest.TwilioException as e:
        print e
#End Functions


#Schedules:
sched = BlockingScheduler()
#sched.start() #sched start when using backgroundscheduler
outboundCall = sched.add_job(MakeCall, 'cron', day_of_week = day, hour = hour, minute = minute) #create job that calls at a specific time

def new_timed_call(minute): #testing job
    @sched.scheduled_job('interval', minutes=minute)
    def timed_job():
        print('testing every so and so minutes.')
        MakeCall()
#End Schedules


#App Portion:
@api.route("/")
def Index(): #load index page that takes in day hour and minute.
    return render_template('Index.html', result = result)

@api.route("/Page2", methods = ['GET', 'POST'])
def Page2(): #load page that takes in phone number, retrieve input from user on desired time
    day = request.form['Day']
    hour = request.form['Hour']
    minute = request.form['Minute']
    sched.reschedule_job('outboundCall', trigger = 'cron', day = day, hour = hour, minute = minute)
    #outboundCall.modify('outboundCall', day = day, hour = hour, minute = minute)
    print day + " " + hour #testing functionality
    result = "Almost there!" #change result message
    return render_template('Page2.html', result = result)#load Final page

@api.route("/Create", methods = ['GET', 'POST'])
def Create(): #final page option 1 (work in progress)
    headline = str(RedditHeadline())
    headline = headline[7:]
    toNumber = request.form['numberInput']
    toNumber = re.sub("\D", "", toNumber)
    if len(toNumber) == 10 or len(toNumber) == 11:
        result = "Your call has been scheduled."
        #MakeCall()
        return render_template('Response.xml', headline = headline, result=result)
    else:
        result = "Please enter a valid number."
        return render_template('Page2.html', result = result)
    #print (toNumber)

@api.route("/add", methods = ['GET', 'POST'])
def add(): #final page option 2 (work in progress)
    day = request.form['Day']
    hour = request.form['Hour']
    minute = request.form['Minute']
    print("test1")
    #sched.reschedule_job('call', trigger = 'cron', day = day, hour = hour, minute = minute)
    outboundCall.modify('outboundCall', day = day, hour = hour, minute = minute)
    print("test2")
    return "scheduled"
#End App Portion


#Start the thing:
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    api.run(host='0.0.0.0', port=port)
    #app.run(debug=True)
    sched.start() #start sched when trying blockingscheduler
