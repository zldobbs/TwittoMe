# TwittoMe
# A final project for CS4830 developed using Flask. Works with the
# Twitter and GroupMe APIs to create a cohesive bot that polls for new
# tweets from user specified accounts.
# Developed by Zachary Dobbs and Austin Sizemore

# --------------- INITIALIZATION AND CONFIG ----
# imports and initiatilization
from flask import Flask, request, render_template, url_for
import tweepy, json, config, time, threading, requests, html
application = Flask(__name__)

# pull config for twitter API (tweepy)
auth = tweepy.OAuthHandler(config.twit['consumer_key'], config.twit['consumer_secret'])
auth.set_access_token(config.twit['access_token_key'], config.twit['access_token_secret'])

# initialize the tweepy api
api = tweepy.API(auth)

# ------------- POLLING THREAD -----------------
# create a thread that will run in the background
# this thread will poll the user's twitter app every 15 seconds
# to check if a new tweet has been posted
# twitter's API restricts the retrieval of data to 10 second intervals
class PollingThread(object):
    # establish thread details
    def __init__(self, interval=15):
        # the interval is the time between polls to the api
        self.interval = interval
        # users will contain the accounts currently being followed
        # defaults to Donald Trump at the start of the server
        # the top parameter specifies the ID of the user's most recent tweet
        self.users = [ {
            'username'  : '@Salvado43061975',
            'top'       : 0 } ]
        # start the thread as a daemon so it does not interrupt normal functionality
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    # method will follow add a new user to the current follow list
    def add_tweeter(self, name):
        # limit the amount of users being followed at one time to 5 users
        if len(self.users) >= 5:
            send_message("A maximum of 5 users may be followed at once! Type #twit unfollow <name> to open a spot")
            return 0
        # keep the data consistent by enforcing an @ character in each username
        if '@' not in name:
            name = '@' + name
        # check if the user is already being followed, don't want a duplicate
        for tweeter in self.users:
            if tweeter['username'].lower() == name.lower():
                send_message("Follow failed! User is already being followed!")
                return 0
        # must try to follow the user
        try:
            api.user_timeline(screen_name = name)
            tweeter = {'username': name, 'top': 0}
            self.users.append(tweeter)
        # if it fails, it means that the username sent was either not real or a private account
        except Exception as e:
            print(e)
            send_message("Follow failed! Please make sure the account name is correct and not private!")

    # method will remove a username from the list of followed users
    def remove_tweeter(self, name):
        # check for an @ character being sent, must maintain data consistency
        if '@' not in name:
            name = '@' + name
        # iterate through the current users, if the user is found then it will be removed
        for index, tweeter in enumerate(self.users):
            if tweeter['username'].lower() == name.lower():
                del self.users[index]
                send_message("Successfully unfollowed " + name + "!")
                return 0
        # if the method doesn't return above, then the user specified was not found
        send_message("User specified is not currently being followed!")

    # method will print all accounts currently being followed
    def list(self):
        # check if noone is being followed
        if len(self.users) == 0:
            msg = "Noone is being followed! Type #twit follow <user> to start following!"
        # if it is not empty, iterate through each user and print their name
        else:
            msg = "Users currently being followed: "
            for tweeter in self.users:
                msg = msg + tweeter['username'] + ' '
        send_message(msg)

    # method that will poll for a new tweet for a given user
    def query_user(self, tweeter):
        # if top is 0, then no tweets for this user have been evaluated yet
        if tweeter['top'] == 0:
            # status will contain the tweet infromation retrieved from the API
            status = api.user_timeline(screen_name = tweeter['username'], count = 1, tweet_mode = 'extended')
            # set top to the id of the tweet. this id increments with each new tweet
            tweeter['top'] = status[0].id
            print("Init: " + html.unescape(status[0].full_text))
            # maintain data consistency by checking for the @ character
            if '@' not in tweeter['username']:
                send_message("Started following @" + tweeter['username'] + "!")
            else:
                send_message("Started following " + tweeter['username'] + "!")
            # send the tweet retrieved
            tweet = status[0]
            send_tweet(tweet)
        # if top is not 0, then some tweet has already been referenced
        else:
            status = api.user_timeline(screen_name = tweeter['username'], count = 1, tweet_mode = 'extended')
            curr = status[0]
            # check if the retrieved tweet is newer than current top tweet
            if curr.id > tweeter['top']:
              print("New tweet! -> " + html.unescape(curr.full_text))
              send_tweet(curr)
              # set the new top to the current tweet
              tweeter['top'] = curr.id

    # method for the looping that will run on the daemon thread
    def run(self):
        # infinite loop, this process should run in the backround continuously
        while True:
            # for each user being followed, poll for their most recent tweet
            for tweeter in self.users:
                self.query_user(tweeter)
            # wait 15 seconds before checking again
            # twitter API requires at least 10 seconds between queries
            print('polling...')
            time.sleep(self.interval)

# start the polling!
poll = PollingThread()

# method will send the tweet infromation to GroupMe via bot
def send_tweet(status):
    # set the name and message
    name = status.user.name
    msg = html.unescape(status.full_text)
    send_message(name + ": " + msg)

# --------------- GROUPME BOT ------------------
# sends the specified message to the GroupMe chat
def send_message(msg):
    print('Attempting to send: ' + msg)
    # uses a post request to send to the chat
    # the bot's ID is stored in an external config file
    r = requests.post('https://api.groupme.com/v3/bots/post', data = {"text" : msg, "bot_id" : config.meBot['bot_id']})

# --------------- ROUTES -----------------------
# handle the display page of the applicaiton
@application.route("/", methods=['GET'])
def index():
	return render_template('home.html')

@application.route("/home", methods=['GET'])
def home():
	return render_template('home.html')

@application.route("/tech", methods=['GET'])
def tech():
	return render_template('tech.html')

@application.route("/instructions", methods=['GET'])
def instructions():
	return render_template('instructions.html')

# handle the callback of messages sent from the group chat
@application.route("/msg", methods=['POST'])
def handle():
    # get the message sent in json format
    data = request.get_json()
    # make sure that the the message sent is from an actual user and not the bot
    # #twit will denote the signal for a bot command
    if data['name'] != 'TwittoBot' and '#twit' in data['text']:
        # parse the received message for a valid command
        tokens = data['text'].split()
        # default to the error message, will change if a valid command is found
        msg = "Sorry, I didn't recognize that command. Try typing '#twit help' to list available commands"
        # commands
        if tokens[1]:
            command = tokens[1]
            # help will display some basic information on the application
            if command == 'help':
                msg = "Follow your favorite accounts to receive realtime updates on new tweets! Some available commands: "
                msg = msg + "follow <user>, unfollow <user>, list"
            # follow will add a user to the follow list
            if command == 'follow':
                # check if a username was specified
                if not tokens[2]:
                    msg = "You must specify a valid public user to follow!"
                # try to follow the specified user
                else:
                    msg = ""
                    poll.add_tweeter(tokens[2])
            # list will display all users being followed
            if command == 'list':
                msg = ""
                poll.list()
            # unfollow will remove a user from the follow list
            if command == 'unfollow':
                # check if a username was specified
                if not tokens[2]:
                    msg = "You must specify a user to unfollow!"
                # try to unfollow the specified user
                else:
                    msg = ""
                    poll.remove_tweeter(tokens[2])
        # send a message to the chat, will either be an error or success response
        send_message(msg)
        print("Original message sent -> " + data['text'])
    return "Righteous!"

# --------------- SERVER START -----------------
if __name__ == "__main__":
	# 8080 port is allowed inbound on AWS
	application.run(host='0.0.0.0', port='8080')
