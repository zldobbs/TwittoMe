# --------------- INITIALIZATION AND CONFIG ----
# imports and initiatilization
from flask import Flask, request
# from urllib.parse import urlencode
# from urllib.request import Request, urlopen
import tweepy, json, config, time, threading, requests, html
application = Flask(__name__)

# pull config for twitter API (tweepy)
auth = tweepy.OAuthHandler(config.twit['consumer_key'], config.twit['consumer_secret'])
auth.set_access_token(config.twit['access_token_key'], config.twit['access_token_secret'])

api = tweepy.API(auth)

# ------------- POLLING THREAD -----------------
# create a thread that will run in the background
# this thread will poll the user's twitter app every 15 seconds
# to check if a new tweet has been posted
class PollingThread(object):
    def __init__(self, interval=15):
        # establish thread details
        self.interval = interval
        # create an option to change the followed user via the GroupMe bot
        self.username = 'realDonaldTrump'
        # initiate the first tweet to null
        self.top = 0
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def set_username(self, name):
        try:
            api.user_timeline(screen_name = name)
            self.top = 0
            self.username = name
        except Exception:
            send_message("Follow failed! Please make sure the account name is correct and not private!")

    def run(self):
        # where the actual polling will take place
        while True:
            if self.top == 0:
                # pull the user's most recent tweet to reference against
                status = api.user_timeline(screen_name = self.username, count = 1, tweet_mode = 'extended')
                self.top = status[0]
                print("Init: " + html.unescape(self.top.full_text))
                if '@' not in self.username:
                    # account for both methods some person may input a username during follow
                    send_message("Started following @" + self.username + "!")
                else:
                    send_message("Started following " + self.username + "!")
                send_message(self.top.user.name + ": " + html.unescape(self.top.full_text))
                print(self.top.id)
            else:
                status = api.user_timeline(screen_name = self.username, count = 1, tweet_mode = 'extended')
                curr = status[0]
                print(curr.id)
                # check if the retrieved tweet is newer than the current recent
                if curr.id > self.top.id:
                  print("New tweet! -> " + html.unescape(curr.full_text))
                  send_message(curr.user.name + ": " + html.unescape(curr.full_text))
                  self.top = curr
            # wait 15 seconds before checking again
            # twitter API requires at least 10 seconds between queries
            time.sleep(self.interval)

# start the polling!
poll = PollingThread()

# -------------- STREAM -----------------------
# create a stream to listen to tweets coming in
# class MyStreamListener(tweepy.StreamListener):
# 	def on_status(self, status):
# 		print(status.text)

# initialize the stream, this isn't really doing anything at the moment
# myStreamListener = MyStreamListener()
# myStream = tweepy.Stream(auth = api.auth, listener = myStreamListener)
# myStream.filter(follow=['espn', async=True)

# --------------- GROUPME BOT -----------------
def send_message(msg):
    # POST to the GroupMe chat
    print('Attempting to send: ' + msg)
    r = requests.post('https://api.groupme.com/v3/bots/post', data = {"text" : msg, "bot_id" : config.meBot['bot_id']})

# --------------- ROUTES ----------------------
# route for display page of the applicaiton
# not too much functionality needed here
@application.route("/", methods=['GET'])
def index():
	user = api.get_user('twitter')
	print(user.screen_name + " API is functioning correctly!")
	return "Everything is operational! Yippee!"

# receive messages from the GroupMe Bot
@application.route("/msg", methods=['POST'])
def handle():
    # do something
    data = request.get_json()
    if data['name'] != 'TwittoBot' and '#twit' in data['text']:
        # create a switch..case under @twit to handle the various commands
        # turns out python doesn't have switch..case statements..
        tokens = data['text'].split()
        msg = "Sorry, I didn't recognize that command. Try typing '#twit help' to list available commands"
        if tokens[1]:
            command = tokens[1]
            if command == 'help':
                # display help information
                msg = "The TwittoBot is still under development. Some commands you can use: help, follow <user>"
            if command == 'follow':
                # follow a new user
                if not tokens[2]:
                    msg = "You must specify a valid public user to follow!"
                else:
                    msg = ""
                    poll.set_username(tokens[2])
        send_message(msg)
        print("Original message sent -> " + data['text'])
    return "Righteous!"

# --------------- SERVER START ------------------
if __name__ == "__main__":
	# 8080 port is allowed inbound on AWS
	# try 0.0.0.0 as host for now, if it doesn't work switch to the ip of AWS
	application.run(host='0.0.0.0', port='8080')
