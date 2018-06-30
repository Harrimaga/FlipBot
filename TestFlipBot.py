import discord
import pickle
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
import datetime
import threading

# Tell the bot that he's actually a discord user
Client = discord.Client()
client = commands.Bot(command_prefix = "!")

# Used for declaring the dictionaries
firstItems = {}

# Declaring empty dictionaries to read/write data from/to
global NotificationTable
NotificationTable = dict.fromkeys(firstItems)

global TimeTable
TimeTable = dict.fromkeys(firstItems)

global HistoryTable
HistoryTable = dict.fromkeys(firstItems)

# 2 lists used for specific functions
global Silence
Silence = []

global Recent
Recent = []

# When the bots starts up it reads the dictionaries from binary files saved in the bot's location
# Because the bot can stop running at random moments saving/loading the data has to be used
# The way I implemented it made it so that every server the bot is in has the same data
# This is fine for now, but not optimal
with open("NotificationTable.txt", "rb") as in_file:
    NotificationTable = pickle.load(in_file)
with open("HistoryTable.txt", "rb") as his_in_file:
    HistoryTable = pickle.load(his_in_file)
with open("SilenceList", "rb") as f:
    Silence = pickle.load(f)
with open("TimeTable", "rb") as t:
    TimeTable = pickle.load(t)

#print (NotificationTable)

# Function to send a notification if a limit has expired for someone
async def checkLimits():
    await client.wait_until_ready()
    while not client.is_closed:
        Removables = []
        SentMessages = []
        global TimeTable

        # For each given report, check if it's been 4 hours. If it has, send a notification and remove the entry
        for user in TimeTable:
            for times in TimeTable[user]:

                # Calculate time
                start = times[1]
                end = datetime.datetime.utcnow()
                diff = end - start

                # Check if it's been 4 hours
                if diff.seconds / 60 >= 240:
                    usr = await client.get_user_info(user)
                    msg = user + "'s limit has expired of " + times[0]

                    # The following if-statement was made to work around a bug that isn't occuring any more
                    if msg not in SentMessages:
                        await client.send_message(usr, "Your limit on **" + times[0] + "** has expired!")
                        print(user + "'s limit has expired of " + times[0])
                        SentMessages.append(msg)
                    
                    # Because I foreach over the data, I have to remove entries from said data OUTSIDE of the foreach
                    # So in removables I keep track of which entries should be removed
                    Removables.append([user, times[0]])

        # Remove each entry that had a notification sent already
        for rem in Removables:
            for times in TimeTable[rem[0]]:
                if times[0] == rem[1]:
                    TimeTable[rem[0]].remove(times)

        # Save the data to a binary file, in case of bot crash
        with open("TimeTable", "wb") as q:
                pickle.dump(TimeTable, q)

        # Only do this check every 5 minutes to keep my subscribtion cost low ^.^
        await asyncio.sleep(300)



@client.event
# If the bot is ready after start-up
async def on_ready():
    print("Bot is ready!")

    # Sets the "playing" status to "Streaming" with "!n [item] nib [msg]" in the text and a link to my twitch
    await client.change_presence(game=discord.Game(name="!n [item] nib [msg]", url="https://twitch.tv/Batsphemy", type=1))

@client.event
# If the bot receives a message
# I know there are other very good ways to handle commands and I will be checking them out later
# This is just a very easy way to get commandhandling done
async def on_message(message):

    global NotificationTable
    global HistoryTable

    # If the bot is the sender of the message, don't do anything with it
    if message.author == client.user:
        return

##    if message.content.upper().startswith('!PING'):
##        userID = message.author.id
##        await client.send_message(message.channel, "<@%s> Pong" % (userID))

    # The try is here in case something REALLY bad happens but now the bot won't shut down yeuy!
    try:

        # Basically a command is a 'message.content.upper()' check
        # If the message content (or arguments of the content if the string is split) matches a certain combination, it calls a command

        # Immature, unneeded commands that I forgot I implemented
        if message.content.upper() == "AYY":
            await client.send_message(message.channel, "Lmao")

        if message.content.upper().startswith("UR MOM") or message.content.upper().startswith("YOUR MOM") or message.content.upper().startswith("UR MUM") or message.content.upper().startswith("YOUR MUM"):
            await client.send_message(message.channel, "LMAOOO!!")

        if message.content.upper() == "KAMEHAME":
            await client.send_message(message.channel, "HAAAAAAAAAAAAAAAAAAAAAAAAAA!!!!")

        # Tests the notification function (mainly the time test)
        if message.content.upper() == "PRINTTIMETEST":
            for user in TimeTable:
                for times in TimeTable[user]:
                    start = times[1]
                    end = datetime.datetime.utcnow()
                    diff = end - start
                    if diff.seconds / 60 >= 0:
                        print(user + " " + times[0])

        # Splits the message string into a list 'args', on " " (so every word is an entry in args)
        args = message.content.split(" ")

        # Subscribe function
        if args[0].upper() == "!SUBSCRIBE" or args[0].upper() == "!S":

            # For-loop to make multiple item subscribtion possible
            for i in range(1, len(args)):

                # If the item already exists as an item in the dictionairy the player needs to be added to that list (if the player isn't already subscribed to that item)
                # If the item does NOT exist in the dictionairy, a new key should be made with the player as value
                if args[i] in NotificationTable:
                    players = NotificationTable[args[i]]

                    # If the player is not subscribed to the item, subscribe them and send a confirmation
                    if message.author.id not in players:
                        players.append(message.author.id)
                        await client.send_message(message.channel, "%s is now subscribed to %s" % (message.author.name, args[i]))

                    # Error message otherwise
                    else:
                        await client.send_message(message.channel, "You are already subscribed to the item: %s" % (args[i]))
                
                # New item entry
                else:
                    players = []
                    players.append(message.author.id)
                    NotificationTable[args[i]]= players
                    await client.send_message(message.channel, "%s is now subscribed to %s" % (message.author.name, args[i]))
            #print(NotificationTable)

            # Save data!
            with open("NotificationTable.txt", "wb") as out_file:
                pickle.dump(NotificationTable, out_file)

        # Function for notifying subscribed players of a report
        if args[0].upper() == "!NOTIFY" or args[0].upper() == "!N":

            # If the item is in the dictionairy as key, notify all players
            if args[1] in NotificationTable:
                players = NotificationTable[args[1]]
                messg = ""

                for player in players:
                    
                    # Players in the Silence list don't want notifications, so don't send them!
                    if player not in Silence:

                        # Get the user object from the userid
                        user = await client.get_user_info(player)

                        # Add all the args after the itemname back into 1 string
                        mess = " ".join(args[2:])

                        # Send different notifications based on whether there was a message or just a report
                        if len(args) < 3:
                            messg = "[%s:%02d] **%s** by %s" % (message.timestamp.hour, message.timestamp.minute, args[1], message.author.name)
                        else:
                            messg = "[%s:%02d] **%s** by %s: %s " % (message.timestamp.hour, message.timestamp.minute, args[1], message.author.name, mess)

                        # Try to send a message. This can give an exception when the user has disabled pms
                        try:
                            await client.send_message(user, messg)
                        except:
                            print("%s has disabled pm" % (user.name))

                # Adding reports to items so we can get the 5 latest reports via a command 
                # If the item does not have a history yet, create a new one        
                if args[1] not in HistoryTable:

                    # Add the report to the recent reports for that item
                    history = []
                    history.append(messg)
                    HistoryTable[args[1]] = history

                # Workaround to fix reports showing up multiple times
                elif messg not in HistoryTable[args[1]]:
                    history = HistoryTable[args[1]]

                    # Make the history be only 5 reports long
                    if len(history) > 4:
                        history.pop(0)
                    history.append(str(message.timestamp.date()) + " " + messg)

                # Add report to recent list (again with the workaround)
                if messg not in Recent:
                    if len(Recent) > 4:
                        Recent.pop(0)
                    Recent.append(str(message.timestamp.date()) + " " + messg)

                # Save data!
                with open("HistoryTable.txt", "wb") as his_out_file:
                    pickle.dump(HistoryTable, his_out_file)
                with open("RecentList", "wb") as f:
                    pickle.dump(Recent, f)

                # If the report was a buy, that person is on limit for 4 hours, so they should be added to the TimeTable for that item
                if args[2].upper() == "NIB":
                    if message.author.id not in TimeTable:
                        times = []
                        itemTime = [args[1], message.timestamp]
                        times.append(itemTime)
                        TimeTable[message.author.id] = times
                    else:
                        found = "false"

                        # Only add to timetable if there is no older report already present for that item/user combination
                        for times in TimeTable[message.author.id]:
                            if times[0] == args[1]:
                                found = "true"
                        if found == "false":
                            itemTime = [args[1], message.timestamp]
                            TimeTable[message.author.id].append(itemTime)

                # Save data!
                with open("TimeTable", "wb") as q:
                    pickle.dump(TimeTable, q)


        # Function to test timetable functionality
        if args[0].upper() == "PRINTTIMETABLE":
            print(TimeTable)

        # Returns the ping
        if args[0].upper() == "PING":
            pingtime = time.time()
            pingms = await client.send_message(message.channel, "*Pinging...*")
            ping = (time.time() - pingtime) * 1000
            await client.edit_message(pingms, "**Pong!** :ping_pong:  The ping time is `%dms`" % ping)
            print("Pinged bot with a response time of %dms." % ping)


        # unsubscribe from an item
        if args[0].upper() == "!UNSUBSCRIBE" or args[0].upper() == "!US":

            # If the item is 'All' unsubscribe from all items
            if args[1].upper() == "ALL":
                for players in NotificationTable.values():
                    if message.author.id in players:
                        players.remove(message.author.id)
                        #print(NotificationTable)
                await client.send_message(message.channel, "You have been unsubscribed from all items")

            # If the item is in their notification table, remove it
            if args[1] in NotificationTable:
                players = NotificationTable[args[1]]
                players.remove(message.author.id)
                #print(NotificationTable)
                await client.send_message(message.channel, "You have been unsubscribed from %s" % (args[1]))

            # Save data!
            with open("NotificationTable.txt", "wb") as out_file:
                pickle.dump(NotificationTable, out_file)

        # Lists all the items you are subscribed to
        if args[0].upper() == "MYSUBS" or args[0].upper() == "!M":
            items = []

            for item in NotificationTable.keys():
                if message.author.id in NotificationTable[item]:
                    items.append(item)

            mess = ", ".join(items[:])
            if items == []:
                await client.send_message(message.channel, "You are not subscribed to any items")
            else:
                text = "You are subscribed to: %s" % (mess)
                await client.send_message(message.channel, text)

        # Prints the 5 most recent reports for a given item
        if args[0].upper() == "!HISTORY" or args[0].upper() == "!H":
            try:
                messages = HistoryTable[args[1]]
                mess = ""
                for x in range(0, len(messages)):
                    mess += messages[x] + "\n"
                await client.send_message(message.channel, mess)
            except:
                await client.send_message(message.channel, "There is no history of this item!")

        # Prints the commandlist
        if args[0].upper() == "!HELP" or args[0].upper() == "!COMMANDS":

            text = "These are the commands for the FlipBot: \nAnywhere it says [item] you should replace it with the item you are refering to (like: !subscribe swh)\n\n'!subscribe [item]' *alias: '!s'* -> Adds you to the notification list for item[item]\n'!unsubscribe [item]' *alias '!us'* -> Removes you from the notification list for item [item]\n'!unsubscribe all' -> Removes you from all notification lists\n'!mysubs' *alias '!m'* -> Shows which items you are subscribed to\n'!notify [item] [message]' *alias '!n'* -> Notifies everyone that is subscribed to item[item] and also sends them a message:\nUsage: '!notify swh nib 96.9' -> Notifies the following message: You have been notified for the item: swh by [caller of the command]: nib 96.9 at: [UTC time when the notify was send]'\n\n'!commands' *alias '!help'* -> sends this message!"
            try:
                await client.send_message(message.author, text)
            except:
                await client.send_message(message.channel, "You have disabled pm")
                print("%s has disabled pms!" % (message.author))

        # Adds the user to the silence list so they won't get notifications 
        # OR removes the user if they are already in the silence list
        if args[0].upper() == "!SILENCE":
            if message.author.id in Silence:
                Silence.remove(message.author.id)
                await client.send_message(message.channel, "You will get notifications again")
                with open("SilenceList", "wb") as f:
                    pickle.dump(Silence, f)
            else:
                Silence.append(message.author.id)
                await client.send_message(message.channel, "You will not get notifications again untill this command is called again.")
                with open("SilenceList", "wb") as f:
                    pickle.dump(Silence, f)

        # Print the 5 most recent reports
        if args[0].upper() == "!RECENT" or args[0].upper() == "!R":
            m = ""
            for q in Recent:
                m += q + "\n"
            await client.send_message(message.channel, m)

        # Testfunctions to force save and load
        if args[0].upper() == "!SAVE" and message.author.id == "My ID":
            with open("NotificationTable.txt", "wb") as out_file:
                pickle.dump(NotificationTable, out_file)
            with open("HistoryTable.txt", "wb") as his_out_file:
                pickle.dump(HistoryTable, his_out_file)
                print("save")
            with open("RecentList", "wb") as f:
                pickle.dump(Recent, f)

        if args[0].upper() == "!LOAD" and message.author.id == "My ID":
            with open("NotificationTable.txt", "rb") as in_file:
                NotificationTable = pickle.load(in_file)
            with open("HistoryTable.txt", "rb") as his_in_file:
                HistoryTable = pickle.load(his_in_file)
                print("load")

        # PMs the user all items that are currently in the itemlist (AKA have at some point been, or still are, subscribed by an user)
        if args[0].upper() == "!ITEMLIST":
            items = ""

            for item in NotificationTable.keys():
                items += item + "\n"
            try:
                await client.send_message(message.author, items)
            except:
                print("%s has disabled pm" % (user.name))
        SentMessages = []
    except:
        # Python NEEDED actual code in except sadface
        fqwe = "lulz"

# Run the loop for checking limits
client.loop.create_task(checkLimits())
client.run("-----") # Your discord bot's client key here