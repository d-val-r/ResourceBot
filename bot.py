from bs4 import BeautifulSoup as bs
import imaplib, ssl, re, discord
from email.message import EmailMessage

# credentials omitted
user = ""
password = ""

hostname = "outlook.office365.com"

# creates a security context
context = ssl.create_default_context()
conn = imaplib.IMAP4_SSL(host=hostname, ssl_context=context)

conn.login(user, password)

# set readOnly flag to true during testing to avoid 
# potential corrupting emails
conn.select("Inbox", readonly=True)


# find all emails from Quincy Larson; the second return 
# (the one stored in data) is the result list
typ, data = conn.search(None, "FROM", "quincy@freecodecamp.org")


# set up lists for later use
emails = []
link_results = []
links = []

# the way the datatype in the data variable is stored requires that
# the first item in the container be split to access emails
for email in data[0].split():
    
    # grab an email and store it in result
    typ, result = conn.fetch(email, '(RFC822)')

    # result[0][1] is the body of the email in byte form
    emails.append(result[0][1].decode())

# the connection to the email is no longer necessary
conn.close()
conn.logout()

# for some reason, the emails have a quirk where the body is separated by
# a sequence of characters, '=\r\n' instead of a typical newline
for i in range(len(emails)):

    # split by the character pattern and rejoin using an empty string for
    # easier parsing
    emails[i] = "".join(emails[i].split("=\r\n"))

    # use regular expressions to parse the email bodies and append results
    # to the list
    link_results.append(re.findall("(http.*)\s", emails[i]))

# the re.findall() method returns a list, so each item in link_results is
# a list, hence the second for loop
for item in link_results:

    # as of the time that I began receiving emails, Quincy Larson primarily
    # sends 5 links per email; the FIRST five are the relevant ones
    for i in range(5):
        links.append(item[i])

# start the discord client
client = discord.Client()
channels = {}

@client.event
async def on_ready():
    # prints a ready message to the console -- for use when I was testing locally
    print("{0.user} ready for orders, captain!".format(client))

    # loop through the channels on the server and fill out the channels dictionary
    # using a key-value pair of channel-name and channel-id
    for channel in client.get_all_channels():

        # the get_all_channels method reads the "Text\Voice Channels" label,
        # so the goal is to avoid processing the labels
        if (channel != "Text Channels" and channel != "Voice Channels"):
            channels[channel.name] = channel.id


@client.event
async def on_message(message):

    # prevents the bot from response to its own messages
    if message.author == client.user:
        return

    # update on demand from a user
    elif(message.content == "$update"):
        for link in links:
            await client.get_channel(channels['bot-resource-test']).send(link)

# bot token omitted
client.run('')
