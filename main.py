# --------------- INITIALIZATION AND CONFIG ----
# imports and initiatilization
from flask import Flask, request, render_template, url_for
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
        # create an option to change the followed user via the GroupMe bot -- done
        # make the username an array, call the poll on each username
        self.users = [ {
            'username'  : '@realDonaldTrump',
            'top'       : 0 } ]
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def add_tweeter(self, name):
        # add a username to the users
        if len(self.users) >= 5:
            send_message("A maximum of 5 users may be followed at once! Type #twit unfollow <name> to open a spot")
            return 0
        if '@' not in name:
            name = '@' + name
        for tweeter in self.users:
            if tweeter['username'].lower() == name.lower():
                send_message("Follow failed! User is already being followed!")
                return 0
        try:
            api.user_timeline(screen_name = name)
            tweeter = {'username': name, 'top': 0}
            self.users.append(tweeter)
        except Exception as e:
            print(e)
            send_message("Follow failed! Please make sure the account name is correct and not private!")

    def remove_tweeter(self, name):
        # remove username from users
        if '@' not in name:
            name = '@' + name
        for index, tweeter in enumerate(self.users):
            if tweeter['username'].lower() == name.lower():
                del self.users[index]
                send_message("Successfully unfollowed " + name + "!")
                return 0
        send_message("User specified is not currently being followed!")

    def list(self):
        # list all usernames in usernames
        if len(self.users) == 0:
            msg = "Noone is being followed! Type #twit follow <user> to start following!"
        else:
            msg = "Users currently being followed: "
            for tweeter in self.users:
                msg = msg + tweeter['username'] + ' '
        send_message(msg)

    def query_user(self, tweeter):
        # check for the new tweet
        if tweeter['top'] == 0:
            # pull the user's most recent tweet to reference against
            status = api.user_timeline(screen_name = tweeter['username'], count = 1, tweet_mode = 'extended')
            tweeter['top'] = status[0].id
            print("Init: " + html.unescape(status[0].full_text))
            if '@' not in tweeter['username']:
                # account for both methods some person may input a username during follow
                send_message("Started following @" + tweeter['username'] + "!")
            else:
                send_message("Started following " + tweeter['username'] + "!")
            send_message(status[0].user.name + ": " + html.unescape(status[0].full_text))
        else:
            status = api.user_timeline(screen_name = tweeter['username'], count = 1, tweet_mode = 'extended')
            curr = status[0]
            # check if the retrieved tweet is newer than the current recent
            if curr.id > tweeter['top']:
              print("New tweet! -> " + html.unescape(curr.full_text))
              send_message(curr.user.name + ": " + html.unescape(curr.full_text))
              tweeter['top'] = curr.id

    def run(self):
        # where the actual polling will take place
        while True:
            for tweeter in self.users:
                self.query_user(tweeter)
            # wait 15 seconds before checking again
            # twitter API requires at least 10 seconds between queries
            print('polling...')
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
	return render_template('index.html')

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
                msg = "Follow your favorite accounts to receive realtime updates on new tweets! Some available commands: "
                msg = msg + "follow <user>, unfollow <user>, list" 
            if command == 'follow':
                # follow a new user
                if not tokens[2]:
                    msg = "You must specify a valid public user to follow!"
                else:
                    msg = ""
                    poll.add_tweeter(tokens[2])
            if command == 'list':
                # list all users currently being followed
                msg = ""
                poll.list()
            if command == 'unfollow':
                # unfollow a user currently being followed
                if not tokens[2]:
                    msg = "You must specify a user to unfollow!"
                else:
                    msg = ""
                    poll.remove_tweeter(tokens[2])
        send_message(msg)
        print("Original message sent -> " + data['text'])
    return "Righteous!"

# --------------- SERVER START ------------------
if __name__ == "__main__":
	# 8080 port is allowed inbound on AWS
	# try 0.0.0.0 as host for now, if it doesn't work switch to the ip of AWS
	application.run(host='0.0.0.0', port='8080')
