#TwittoMe

Introduction:

Github: https://github.com/zldobbs/TwittoMe

Instance: http://ec2-54-84-226-34.compute-1.amazonaws.com

Members: Zachary Dobbs, Austin Sizemore
•	Zachary Dobbs: Back End
•	Austin Sizemore: Front End, Documentation

Introduction:
 
  TwittoMe is a web application built to combine the functionalities of Twitter and GroupMe. The application is a GroupMe chat bot that will follow up to 5 specified twitter accounts. Anytime one of these accounts sends out a new tweet, the GroupMe bot will push the tweet into the chat. 
  The inspiration for this project came about during the active shooter threat we experienced earlier this semester. Students were complaining about the lack of communication through the text alert system. We noticed that the MU Alert Twitter account was actually providing much better up to date information. This project would allow those tweets to get pushed to whatever group chat you’re in, preventing the spread of false information that was so prevalent during this time. 
  Other examples of the benefits of this bot are following the New York Stock Exchange to discuss stock fluctuations, Donald Trump to discuss/laugh at politics, or Barstool Mizzou to keep up with all the hot takes from the football game. The possibilities are endless when the power of these two applications are combined through our web app. 




Instructions:

  In order to test the project, you must first join the “Twittering” GroupMe chat. You can do so by following this link: https://web.groupme.com/join_group/36497532/bzHBsx
Once in the chat, you can test the TwittoBot using some commands. To get the bot’s attention you use “#twit” followed by an instruction. The valid commands are:

•	#twit follow <username>
  o	Adds the specified username to the list of accounts being followed. The username must be valid and not a private account. The bot may only follow 5 accounts at one time. 
•	#twit unfollow <username>
  o	Removes the specified username from the list of accounts being followed.
•	#twit list
  o	Lists all accounts currently being followed
•	#twit help
  o	Displays a simple help message outlining these commands. 
If you follow popular accounts such as realDonaldTrump, ESPN, or TacoBell, you should be able to see tweets being posted to the chat fairly quickly. 
*Note: Following an account may take a few seconds to begin functioning. The follow function works as part of the polling thread that only operates every 15 seconds. Please be patient after using the #twit follow command!

Implementation:

Technologies:
•	Flask (A Python Microframework)
  o	Flask was run through a nginx/Gunicorn server setup. The microframework made it easy for handling all of the URL callbacks and  routing associated with the various API’s used. 
•	HTML
•	CSS
•	Bootstrap
  o	To use its adaptability to different screen sizes along with premade classes to avoid typing up too much CSS code
•	Twitter API
  o	The Twitter API was authenticated and ran using the Tweepy module for Flask. This module made it incredibly simple to manage the polling of user timelines. 
•	GroupMe Bot
  o	The GroupMe bot manages the method to receive messages from users and then post responses to the chat. 

Parts Of Interest:

Back End:

  One of the most difficult parts of developing the backend was finding a way to check the twitter account’s timelines on a regular interval indefinitely without interrupting normal processes. After a lot of research, we settled on implementing a thread that would run as a daemon (background function) while the server was running. This process required a lot of trial and error to get functioning correctly, but in the end we were satisfied to see our product match our vision perfectly. 
  One aspect of the application that could be improved would be finding a way to have the bot send images from tweets as well. At this point, the bot only sends a link to the image if the tweet contains a picture. The issue in getting this to work correctly is that the GroupMe bot will only send images that are hosted through the GroupMe Image Service. The twitter API returns image URL’s when there is media associated with the tweet. The problem arises with getting this image URL onto GroupMe’s Image Service. The Image Service seems to require a binary image data file, so it would require us to download each image received in a tweet to a folder, then upload the data onto the service, then finally send the image with the tweet. This proved just a little too complicated for us to implement before the due date, but it is something we will continue to pursue. Downloading that many images would also have taken a significant toll on the free tier benefits of our AWS instance. 

Front End:

  When it came to designing the front end, I ran into troubles of being unfamiliar with Bootstrap. Upon doing more research into the language, new discoveries or deeper learning on a topic made me to have to go back multiple times and change my CSS code to simplify the styling of the design and to minimalize my code. I used more of the @media rule to help with responsiveness of the page. 
  Problems I faced was indecisiveness and that I would not like how I was going about designing the site. This would restart too many times when I should have settled on a design. Additionally, I was able to make the site decently responsive but many changes could be made to increase the responsiveness. This could be achieved Bootstrap’s grid system and also using its version of the @media rule. Utilizing further animations would be ideal such as page switching transitions or scrolling effects such as parallax.

Conclusion:

  During the development of this project, both members of our group learned much during the project’s creation. The technology used was known to us beforehand but we learned many new techniques and really dove into the technologies to learn more about them. There were many roadblocks that were hit along the way when learning new things and trying to solve them. We ended up crafting a project that can be used on a regular basis for our personal use and for our friends as well and are happy with what we made.
