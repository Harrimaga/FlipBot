import discord
from discord.ext.commands import Bot
from discord.ext import commands, tasks
from discord.utils import get
import pickle
import asyncio
import random
import time
from datetime import datetime, timedelta, date
import threading
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import twitter

#twitterApi = twitter.Api(consumer_key="TwXavQWfz3alqnv4kjfqMU3mu", consumer_secret="f8UkW5GqEYn2FXLAVGaXOH1V3jGNT9eidCYmzcNa5bh2t5KXlQ", access_token_key="1154545443721924609-3HTv7UFHlbuIL2O04KfzT4sLBs413v", access_token_secret="4QAJP9PRcU9V4iRyJKRAT2Sj5U5hi6cP1iVLn0a1ohv20")

## TODO: Gspread

# Setup client
Client = discord.Client()
client = commands.Bot(command_prefix = "!")

# ======================================
# -------- Achievement Batches ---------
# ======================================

## TODO: Add more batches
AchievementsBatch1 = ["4.png", "16.png", "17.png", "19.png", "20.png", "21.png", "23.png", "24.png", "25.png", "29.png", "31.png", "35.png", "37.png", "38.png", "39.png", "40.png", "45.png", "46.png", "48.png"]
AchievementsBatch2 = ["2.png", "5.png", "6.png", "7.png", "9.png", "10.png", "11.png", "30.png", "32.png", "34.png", "41.png", "49.png", "51.png", "53.png", "55.png", "56.png", "57.png"]


# Batsphemy name change list:
## TODO: maybe read from file?
names = ["Madoka Kanade", "Akemi Homura", "Hachikuji Mayoi", "Kagari Shiina", "Mayuri Shiina", "Kurisu Makise", "63194", "Emma", "Ram", "Rem", "Jashin-Chan", "Senjougahara Hitagi", "Sengoku Nadeko", "Lucy Heartfilia", "Mavis Vermillion", "Tomoe Mami", "Kotonoha Katsure", "Sekai Saionji", "Setsuna Kiyoura", "Toshinou Kyouko", "Akari Akaza", "Chinatsu Yoshikawa", "Ayano Sigiura", "Urara Shiraishi", "Nene Odagiri", "Miyabi Itou"]

# ======================================
# ------------- Load data --------------
# ======================================

# Create Fields

firstItems = {}

global NotificationTable
NotificationTable = dict.fromkeys(firstItems)
global TimeTable
TimeTable = dict.fromkeys(firstItems)
global HistoryTable
HistoryTable = dict.fromkeys(firstItems)
global AdjustTable
AdjustTable = dict.fromkeys(firstItems)
global ReportCount
ReportCount = dict.fromkeys(firstItems)
global HistoryCount
HistoryCount = dict.fromkeys(firstItems)
global Reminders
Reminders = dict.fromkeys(firstItems)
global ItemList
ItemList = dict.fromkeys(firstItems)

global Silence
Silence = []
global AdjustSilence
AdjustSilence = []
global Recent
Recent = []
global JoinList
JoinList = []

global DailyReports
DailyReports = 0
global TotalReportCount
TotalReportCount = 0

global Today
Today = datetime.today().date()

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('TGEJson.json', scope)
gc = gspread.authorize(credentials)
workSheet = gc.open("CurrentReportList").worksheet("Items")
global newFlipperItems
newFlipperItems = workSheet.col_values(3)[1:]
global intermediateItems
intermediateItems = workSheet.col_values(6)[1:]
global experiencedItems
experiencedItems = workSheet.col_values(9)[1:]
global bulkItems
bulkItems = workSheet.col_values(12)[1:]

# Load data into fields
with open("Joinlist", "wb") as out_jl:
    pickle.dump(JoinList, out_jl)
with open("Reminders", "rb") as in_rem:
    Reminders = pickle.load(in_rem)
with open("Joinlist", "rb") as in_jl:
    JoinList = pickle.load(in_jl)
with open("TodayDate", "rb") as in_date:
    Today = pickle.load(in_date)
with open("AdjustTableBig", "rb") as at:
    AdjustTable = pickle.load(at)
with open("NotificationTableBig.txt", "rb") as in_file:
    NotificationTable = pickle.load(in_file)
with open("HistoryTableBig.txt", "rb") as his_in_file:
    HistoryTable = pickle.load(his_in_file)
with open("SilenceListBig", "rb") as f:
    Silence = pickle.load(f)
with open("AdjustSilenceListBig", "rb") as q:
    AdjustSilence = pickle.load(q)
with open("TimeTableBig", "rb") as t:
    TimeTable = pickle.load(t)
with open("ReportCountBig", "rb") as r:
    ReportCount = pickle.load(r)
with open("HistoryCountBig", "rb") as hc:
    HistoryCount = pickle.load(hc)
with open("ItemListBig", "rb") as i:
    ItemList = pickle.load(i)
with open("DailyReports", "rb") as e:
    DailyReports = pickle.load(e)
with open("TotalReportCount", "rb") as trc:
    TotalReportCount = pickle.load(trc)

if TotalReportCount == 0:
    TotalReportCount = 1

# ==============================
# ------- Repeating Loop -------
# ==============================

@tasks.loop(seconds=60.0)
async def Loop():

    global DailyReports
    global Today
    global Reminders

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('TGEJson.json', scope)
    gc = gspread.authorize(credentials)
    workSheet = gc.open("CurrentReportList").worksheet("Items")

    # =======================
    # --- New day checker ---
    # =======================
    if Today < datetime.today().date():
        print("New Day!")

        # Send report count to admin botspam
        await client.get_guild(465889718349856779).get_channel(466614086340313088).send(content="{}\n\n**Total reports today:** {}".format(str(Today), str(DailyReports)))

        # Reset daily counter
        Today = datetime.today().date()
        DailyReports = 0

        # Save reports and date
        with open("DailyReports", "wb") as e:
            pickle.dump(DailyReports, e)
        with open("TodayDate", "wb") as t:
            pickle.dump(Today, t)

        # Change batto name:
        Server = client.get_guild(465889718349856779)
        Batto = Server.get_member_named("Batsphemy#1337")
        await Batto.edit(nick=random.choice(names))

    # ========================
    # ------ Check VoS -------
    # ========================

#        statuses = []
#        statuses = twitterApi.GetUserTimeline(3429940841)

#        found = False
#        i = 0

#        while(i < 6 and found == False):
#            if statuses[i].text.startswith("The Voice of Seren is now active in the"):
#                found = True;
#                words = statuses[i].text.split(" ")
#                await client.change_presence(game=discord.Game(name="VoS: " + words[9] + " & " + words[11], url="https://twitch.tv/Batsphemy", type=1))
#                i += 1

    # ========================
    # ----- Check Limits -----
    # ========================

    Removables = []
    SentMessages = []
    global TimeTable
    for user in TimeTable:
        for times in TimeTable[user]:
            start = times[1]
            end = datetime.utcnow()
            diff = end - start
            if diff.seconds / 60 >= 240:
                usr = await client.get_user(user)
                msg = user + "'s limit has expired of " + times[0]
                if msg not in SentMessages:
                    try:
                        await usr.dm_channel.send("Your limit on **" + times[0] + "** has expired!")
                        SentMessages.append(msg)
                    except:
                        print(usr.name + " has disabled pms.")
                Removables.append([user, times[0]])

    for rem in Removables:
        for times in TimeTable[rem[0]]:
            if times[0] == rem[1]:
                TimeTable[rem[0]].remove(times)

    with open("TimeTableBig", "wb") as q:
            pickle.dump(TimeTable, q)

    Removables = []
    for user in Reminders:
        for reminder in Reminders[user]:
            start = reminder[0]
            end = datetime.utcnow()
            diff = end - start

            if len(reminder) > 0 and diff.seconds / 60 >= reminder[1]:
                await user.dm_channel.send("***Reminder %s [%s:%02d]:*** %s" %(str(reminder[3].date()), reminder[3].hour, reminder[3].minute, reminder[2]))
                Removables.append([user, reminder])

    for rem in Removables:
        Reminders[rem[0]].remove(rem[1])

    with open("Reminders", "wb") as out_rem:
        pickle.dump(Reminders, out_rem)

async def SubscribeToItem(context, item):
    if item in NotificationTable:
        players = NotificationTable[item]
        if context.message.author.id not in players:
            players.append(context.message.author.id)
            await context.message.channel.send("{} is now subscribed to **{}**".format(context.message.author.name, item))
        else:
            await context.message.channel.send("You are already subscribed to the item **{}**".format(item))
    else:
        players = []
        players.append(context.message.author.id)
        NotificationTable[item] = players
        await context.message.channel.send("{} is now subscribed to **{}**".format(context.message.author.name, item))

def CheckItem(item, user):
    global newFlipperItems
    global bulkItems
    global intermediateItems
    global experiencedItems

    member = client.get_guild(465889718349856779).get_member(user)

    if member == None:
        return False

    roles = []
    for role in member.roles:
        roles.append(role.name)

    if (item in newFlipperItems or item in bulkItems) and ("New Flipper" in roles or "Intermediate Flipper" in roles or "Experienced Flipper" in roles or "Expert Flipper" in roles or "Trial Rank" in roles):
        return True

    if item in intermediateItems and ("Experienced Flipper" in roles or "Intermediate Flipper" in roles or "Expert Flipper" in roles or "Trial Rank" in roles):
        return True

    if item in experiencedItems and ("Experienced Flipper" in roles or "Expert Flipper" in roles or "Trial Rank" in roles):
        return True
    return False


async def AdjustItem(context, item, args):

    m = " ".join(args[1:])
    if len(args) < 3:
        messg = "[%s:%02d] **%s** by %s" % (context.message.created_at.hour, context.message.created_at.minute, item, context.message.author.name)
    else:
        messg = "[%s:%02d] **%s** by %s: %s " % (context.message.created_at.hour, context.message.created_at.minute, item, context.message.author.name, m)

    if item in NotificationTable:
        players = NotificationTable[item]
        for player in players:
            if CheckItem(item, player) == True:
                if player not in AdjustSilence:
                    user = client.get_user(player)
                    if user.dm_channel is not None:
                        await user.dm_channel.send("__Adjust__" + messg)
                    else:
                        await user.create_dm()
                        await user.dm_channel.send(content=messg)
            else:
                print("Removed " + player + " from " + item)
                NotificationTable[item].remove(player)
                with open("NotificationTableBig.txt", "wb") as out_file:
                    pickle.dump(NotificationTable, out_file)

    if item not in AdjustTable:
        adjust = []
        adjust.append(messg)
        AdjustTable[item] = adjust
    elif messg not in AdjustTable[item]:
        adjust = AdjustTable[item]
        if len(adjust) > 4:
            adjust.pop(0)
        adjust.append(str(context.message.created_at.date()) + " " + messg)

    with open("AdjustTableBig", "wb") as atw:
        pickle.dump(AdjustTable, atw)

    await context.message.add_reaction("👍")

async def ReportItem(context, item, args):
    global DailyReports
    global TotalReportCount

    if context.message.author.name not in ReportCount:
        count = 1
        ReportCount[context.message.author.name] = count
    else:
        ReportCount[context.message.author.name] = str(int(ReportCount[context.message.author.name]) + 1)

    DailyReports = DailyReports + 1
    with open("DailyReports", "wb") as e:
        pickle.dump(DailyReports, e)

    messg = ""
    m = " ".join(args[1:])

    if len(args) < 2:
        messg = "[%s:%02d] **%s** by %s" % (context.message.created_at.hour, context.message.created_at.minute, item, context.message.author.name)
    else:
        messg = "[%s:%02d] **%s** by %s: %s " % (context.message.created_at.hour, context.message.created_at.minute, item, context.message.author.name, m)


    if item in NotificationTable:
        players = NotificationTable[item]

        for player in players:
            if CheckItem(item, player) == True:
                if player not in Silence:
                    user = client.get_user(int(player))
                    #try:
                    if user.dm_channel is not None:
                        await user.dm_channel.send(content=messg)
                    else:
                        await user.create_dm()
                        await user.dm_channel.send(content=messg)
                    #except:
                    #    print("{} has disabled pm".format(user.name))
            else:
                print("Removed " + player + " from " + item)
                NotificationTable[item].remove(player)
                with open("NotificationTableBig.txt", "wb") as out_file:
                    pickle.dump(NotificationTable, out_file)

    scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('TGEJson.json', scope)
    gc = gspread.authorize(credentials)
    sheet = gc.open("CurrentReportList").sheet1
    rows = TotalReportCount
    rowValues = [str(context.message.created_at.date()), "%s:%02d" % (context.message.created_at.hour, context.message.created_at.minute), item, context.message.author.name, m, "=B" + str(rows)]
    sheet.insert_row(rowValues, rows, "USER_ENTERED")
    TotalReportCount += 1
    with open("TotalReportCount", "wb") as trcw:
        pickle.dump(TotalReportCount, trcw)

    if item not in HistoryTable:
        history = []
        history.append(messg)
        HistoryTable[item] = history
    elif messg not in HistoryTable[item]:
        history = HistoryTable[item]
        if len(history) > 4:
            history.pop(0)
        history.append(str(context.message.created_at.date()) + " " + messg)

    with open("HistoryTableBig.txt", "wb") as his_out_file:
        pickle.dump(HistoryTable, his_out_file)

    if args[1].upper() == "NIB":
        if context.message.author.id not in TimeTable:
            times = []
            itemTime = [item, context.message.created_at]
            times.append(itemTime)
            TimeTable[context.message.author.id] = times
        else:
            found = "false"
            for times in TimeTable[context.message.author.id]:
                if times[0] == item:
                    found = "true"
            if found == "false":
                itemTime = [item, context.message.created_at]
                TimeTable[context.message.author.id].append(itemTime)
    with open("TimeTableBig", "wb") as q:
        pickle.dump(TimeTable, q)
    with open("ReportCountBig", "wb") as r:
        pickle.dump(ReportCount, r)
    await context.message.add_reaction("👍")

async def CallHistory(context, item):
    if context.message.author.name not in HistoryCount:
        count = 1
        HistoryCount[context.message.author.name] = count
    else:
        HistoryCount[context.message.author.name] = HistoryCount[context.message.author.name] + 1

    with open("HistoryCountBig", "wb") as hc:
        pickle.dump(HistoryCount, hc)

    try:
        messages = HistoryTable[item]
        mess = "__History:__\n"
        for x in range(0, len(messages)):
            mess += messages[x] + "\n"
        try:
            mess += "\n__Adjust:__\n"
            messages = AdjustTable[item]
            for x in range(0, len(messages)):
                y = messages[x]
                mess += y + "\n"
        except:
            print("noAdjusts")
        await context.message.channel.send(content=mess)
    except:
        await context.message.channel.send(content="There is no history of this item!")

@client.event
async def on_member_join(member):
    for mem in JoinList:
        if member.name == mem.name:
            m = ""
            m += "<@&465906826144382986> \n"
            m += "New join " + member.name + " has joined previously. \n"
            m += "Joined at: " + mem.joined_at.strftime("%d/%m/%Y, %H:%M:%S") + "\n"
            m += "Account created at: " + member.created_at.strftime("%d/%m/%Y, %H:%M:%S")
            await client.get_channel(473189355670863882).send_message(m)
    else:
        JoinList.append(member)
        with open("Joinlist", "wb") as out_jl:
            pickle.dump(JoinList, out_jl)

    welcome = ""
    welcome += "Welcome to The Grand Exchangers discord! \n\n"
    welcome += "Make sure to read our rules in " + client.get_channel(521766763256348710).mention + " and press the thumbs up."
    welcome += "Please reach out to a staff member or moderator if you have any questions/need help!"
    await member.dm_channel.send(context=welcome)

# On startup
@client.event
async def on_ready():
    print("Bot is ready!")

    #statuses = []
    #statuses = twitterApi.GetUserTimeline(3429940841)

    found = False
#    i = 0

#    while(i < 6 and found == False):
#        if statuses[i].text.startswith("The Voice of Seren is now active in the"):
#            found = True;
#            words = statuses[i].text.split(" ")
#            await client.change_presence(game=discord.Game(name="VoS: " + words[9] + " & " + words[11], url="https://twitch.tv/Batsphemy", type=1))
#            i += 1

    if found == False:
        stream = discord.Streaming(name="!n [item] nib [msg]", url="https://twitch.tv/Batsphemy")
        await client.change_presence(activity=stream)
    Server = client.get_guild(465889718349856779)
    Batto = Server.get_member_named("Batsphemy#1337")
    await Batto.edit(nick=random.choice(names))

# When a member leaves, remove them from all lists
@client.event
async def on_member_remove(member):
    global NotificationTable
    removables = dict.fromkeys(firstItems)
    for item in NotificationTable:
        for player in NotificationTable[item]:
            if player == member.id:
                if player in removables:
                    removables[player].append(item)
                else:
                    itemlist = []
                    itemlist.append(item)
                    removables[player] = itemlist
    for player in removables:
        for item in removables[player]:
            NotificationTable[item].remove(player)

@client.command(pass_context=True, aliases=["r", "R", "RemindMe"])
async def Reminding(context, *args):
    if len(args) > 1:
        m = " ".join(args[1:])
        ReminderTime = datetime.utcnow()

        try:
            x = int(args[0])
            if context.message.author in Reminders:
                note = [ReminderTime, x, m, context.message.created_at]
                Reminders[context.message.author].append(note)
            else:
                note = [[ReminderTime, x, m, context.message.created_at]]
                Reminders[context.message.author] = note
            await context.message.add_reaction("👍")
        except:
            await context.send("Please provide a time in minutes as the second argument.")

        with open("Reminders", "wb") as out_rem:
            pickle.dump(Reminders, out_rem)

@client.command(pass_context=True, aliases=["S", "s", "SUBSCRIBE"])
async def Subscribe(context, *args):

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('TGEJson.json', scope)
    gc = gspread.authorize(credentials)
    workSheet = gc.open("CurrentReportList").worksheet("Items")
    newFlipperItems = workSheet.col_values(3)[1:]
    intermediateItems = workSheet.col_values(6)[1:]
    experiencedItems = workSheet.col_values(9)[1:]
    bulkItems = workSheet.col_values(12)[1:]
    allItems = newFlipperItems + intermediateItems + experiencedItems + bulkItems

    roles = []
    member = client.get_guild(465889718349856779).get_member(context.message.author.id)
    for role in member.roles:
        roles.append(role.name)

    for item in args:
        if item.endswith(","):
            item = item[:-1]
        if item in allItems:
            if item in newFlipperItems or item in bulkItems:
                if "New Flipper" in roles or "Intermediate Flipper" in roles or "Experienced Flipper" in roles or "Expert Flipper" in roles or "Trial Rank" in roles or "Probation" in roles:
                    await SubscribeToItem(context, item)
                else:
                    await context.send("You need at least the **New Flipper** rank to subscribe to **{}**.\nYou can ask for this role from any moderator/staff member".format(item))

            elif item in experiencedItems:
                if "Experienced Flipper" in roles or "Trial Rank" in roles or "Expert Flipper" in roles or context.message.author.id == 287535385251414017:
                    await SubscribeToItem(context, item)
                else:
                    if ReportCount[context.message.author.name] > 75:
                        await context.send("You need at least the **Experienced Flipper** rank to subscribe to **{}**.\nYou meet the requirements to obtain a Trial Status! For more info see {}.".format(item, client.get_guild(465889718349856779).get_channel(465909830620676118).mention))
                    else:
                        await context.send("You need at least the **Experienced Flipper** rank to subscribe to **{}**.\nFor more information on ranks and their requirements see {}.".format(item, client.get_guild(465889718349856779).get_channel(465909830620676118).mention))
            elif item in intermediateItems:
                if "Intermediate Flipper" in roles or "Experienced Flipper" in roles or "Trial Rank" in roles or "Expert Flipper" in roles or"Expert Flipper" in roles or context.message.author.id == 287535385251414017:
                    await SubscribeToItem(context, item)
                else:
                    await context.send("You need at least the **Intermediate Flipper** rank to subscribe to **{}**.\nFor more information on ranks and their requirements see {}.".format(item, client.get_guild(465889718349856779).get_channel(465909830620676118).mention))
        else:
            print("We don't cover {}.".format(item))
            await context.send("We don't cover **{}**. Let Jayleno know if this is wrong!".format(item))
    with open("NotificationTableBig.txt", "wb") as out_file:
        pickle.dump(NotificationTable, out_file)

@client.command(pass_context=True, aliases=["LIMIT", "L", "l"])
async def Limit(context, *args):
    if len(args) > 0:
        found = "false"
        for itemdate in TimeTable[context.message.author.id]:
            if itemdate[0].upper() == args[0].upper():
                start = itemdate[1] + timedelta(hours=4)
                end = datetime.utcnow()
                diff = start - end
                s = diff.seconds
                hours = s // 3600
                s = s - (hours * 3600)
                minutes = s // 60
                await context.send("Time left till limit expires of **" + args[0] + "**: %s hours and %02d minutes" % (hours, minutes))
                found = "true"
                break
        if found == "false":
            await context.send("You are not on the buylimit of **" + args[0] + "**.")
    else:
        mess = ""
        for itemdate in TimeTable[context.message.author.id]:
            start = itemdate[1] + timedelta(hours=4)
            end = datetime.utcnow()
            diff = start - end
            s = diff.seconds
            hours = s // 3600
            s = s - (hours * 3600)
            minutes = s // 60
            mess +=  "Time left till limit expires of **" + itemdate[0] + "**: %s hours and %02d minutes \n" % (hours, minutes)
        if len(mess) > 0:
            await context.send(mess)
        else:
            await context.send("There's no limit!")

@client.command(pass_context=True, aliases=["ADJUST", "adjust", "A", "a"])
async def Adjust(context, *args):
    if context.message.channel != context.message.author.dm_channel:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('TGEJson.json', scope)
        gc = gspread.authorize(credentials)
        workSheet = gc.open("CurrentReportList").worksheet("Items")
        newFlipperItems = workSheet.col_values(3)[1:]
        intermediateItems = workSheet.col_values(6)[1:]
        experiencedItems = workSheet.col_values(9)[1:]
        bulkItems = workSheet.col_values(12)[1:]
        allItems = newFlipperItems + intermediateItems + experiencedItems + bulkItems

        roles = []
        member = client.get_guild(465889718349856779).get_member(context.message.author.id)
        for role in member.roles:
            roles.append(role.name)

        item = args[0]
        if item in allItems:
            if item in newFlipperItems:
                if "New Flipper" in roles or "Intermediate Flipper" in roles or "Experienced Flipper" in roles or "Expert Flipper" in roles or "Trial Rank" in roles or "Probation" in roles:
                    if context.message.channel.id != 465896717586268162:
                        await context.send("{} Adjustments for **{}** should go in {}".format(context.message.author.mention, item, client.get_guild(465889718349856779).get_channel(465896717586268162).mention))
                        await context.message.delete()
                    else:
                        await AdjustItem(context, item, args)
                else:
                    await context.send("You need at least the **New Flipper** rank to post adjustments for **{}**.\nYou can ask for this role from any moderator/staff member".format(item))
            elif item in bulkItems:
                if "New Flipper" in roles or "Intermediate Flipper" in roles or "Experienced Flipper" in roles or "Expert Flipper" in roles or "Trial Rank" in roles or "Probation" in roles or context.message.author.id == 287535385251414017:
                    if context.message.channel.id != 465893365330739220:
                        await context.send("{} Adjustments for **{}** should go in {}".format(context.message.author.mention, item, client.get_guild(465889718349856779).get_channel(465893365330739220).mention))
                        await context.message.delete()
                    else:
                        await AdjustItem(context, item, args)
                else:
                    await context.send("You need at least the **New Flipper** rank to post adjustments for **{}**.\nYou can ask for this role from any moderator/staff member".format(item))

            elif item in experiencedItems:
                if "Experienced Flipper" in roles or "Trial Rank" in roles or "Expert Flipper" in roles:
                    if context.message.channel.id != 465896763530805248:
                        await context.send("{} Adjustments for **{}** should go in {}".format(context.message.author.mention, item, client.get_guild(465889718349856779).get_channel(465896763530805248).mention))
                        await context.message.delete()
                    else:
                        await AdjustItem(context, item, args)
                else:
                    if ReportCount[context.message.author.name] > 75:
                        await context.send("You need at least the **Experienced Flipper** rank to post adjustments for **{}**.\nYou meet the requirements to obtain a Trial Status! For more info see {}.".format(item, client.get_guild(421820962099429401).get_channel(465909830620676118).mention))
                    else:
                        await context.send("You need at least the **Experienced Flipper** rank to post adjustments for **{}**.\nFor more information on ranks and their requirements see {}.".format(item, client.get_guild(421820962099429401).get_channel(465909830620676118).mention))
            elif item in intermediateItems:
                if "Intermediate Flipper" in roles or "Experienced Flipper" in roles or "Trial Rank" in roles or "Expert Flipper" in roles or"Expert Flipper" in roles or context.message.author.id == 287535385251414017:
                    if context.message.channel.id != 561290453945810954:
                        await context.send("{} Adjustments for **{}** should go in {}".format(context.message.author.mention, item, client.get_guild(465889718349856779).get_channel(561290453945810954).mention))
                        await context.message.delete()
                    else:
                        await AdjustItem(context, item, args)
                else:
                    await context.send("You need at least the **Intermediate Flipper** rank to post adjustments for **{}**.\nFor more information on ranks and their requirements see {}.".format(item, client.get_guild(465889718349856779).get_channel(465909830620676118).mention))

    else:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('TGEJson.json', scope)
        gc = gspread.authorize(credentials)
        workSheet = gc.open("CurrentReportList").worksheet("Items")
        newFlipperItems = workSheet.col_values(3)[1:]
        intermediateItems = workSheet.col_values(6)[1:]
        experiencedItems = workSheet.col_values(9)[1:]
        bulkItems = workSheet.col_values(12)[1:]
        allItems = newFlipperItems + intermediateItems + experiencedItems + bulkItems

        roles = []
        member = client.get_guild(465889718349856779).get_member(context.message.author.id)
        for role in member.roles:
            roles.append(role.name)

        item = args[0]
        if item in allItems:
            if item in newFlipperItems or item in bulkItems:
                if "New Flipper" in roles or "Intermediate Flipper" in roles or "Experienced Flipper" in roles or "Expert Flipper" in roles or "Trial Rank" in roles or "Probation" in roles:
                    await AdjustItem(context, item, args)
                else:
                    await context.send("You need at least the **New Flipper** rank to post adjustments for **{}**.\nYou can ask for this role from any moderator/staff member".format(item))

            elif item in experiencedItems:
                if "Experienced Flipper" in roles or "Trial Rank" in roles or "Expert Flipper" in roles or context.message.author.id == 287535385251414017:
                    await AdjustItem(context, item, args)
                else:
                    if ReportCount[context.message.author.name] > 75:
                        await context.sendy("You need at least the **Experienced Flipper** rank to post adjustments for **{}**.\nYou meet the requirements to obtain a Trial Status! For more info see {}.".format(item, client.get_guild(465889718349856779).get_channel(465909830620676118).mention))
                    else:
                        await context.send("You need at least the **Experienced Flipper** rank to post adjustments for **{}**.\nFor more information on ranks and their requirements see {}.".format(item, client.get_guild(465889718349856779).get_channel(465909830620676118).mention))
            elif item in intermediateItems:
                if "Intermediate Flipper" in roles or "Experienced Flipper" in roles or "Trial Rank" in roles or "Expert Flipper" in roles or"Expert Flipper" in roles or context.message.author.id == 287535385251414017:
                    await AdjustItem(context, item, args)
                else:
                    await context.send("You need at least the **Intermediate Flipper** rank to subscribe to **{}**.\nFor more information on ranks and their requirements see {}.".format(item, client.get_guild(465889718349856779).get_channel(465909830620676118).mention))
        else:
            context.send("We don't cover **{}**. Let Jayleno know if this is wrong!".format(item))

@client.command(pass_context=True, aliases=["NOTIFY", "notify", "N", "n"])
async def Notify(context, *args):
    if context.message.channel != context.message.author.dm_channel:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('TGEJson.json', scope)
        gc = gspread.authorize(credentials)
        workSheet = gc.open("CurrentReportList").worksheet("Items")
        newFlipperItems = workSheet.col_values(3)[1:]
        intermediateItems = workSheet.col_values(6)[1:]
        experiencedItems = workSheet.col_values(9)[1:]
        bulkItems = workSheet.col_values(12)[1:]
        allItems = newFlipperItems + intermediateItems + experiencedItems + bulkItems

        roles = []
        member = client.get_guild(465889718349856779).get_member(context.message.author.id)
        for role in member.roles:
            roles.append(role.name)

        item = args[0]
        if item in allItems:
            if item in newFlipperItems:
                if "New Flipper" in roles or "Intermediate Flipper" in roles or "Experienced Flipper" in roles or "Expert Flipper" in roles or "Trial Rank" in roles or "Probation" in roles or context.message.author.id == 287535385251414017:
                    if context.message.channel.id != 465896717586268162:
                        await context.send("{} Reports for **{}** should go in {}".format(context.message.author.mention, item, client.get_guild(465889718349856779).get_channel(465896717586268162).mention))
                        await context.message.delete()
                    else:
                        await ReportItem(context, item, args)
                else:
                    await context.send("You need at least the **New Flipper** rank to post reports for **{}**.\nYou can ask for this role from any moderator/staff member".format(item))
            elif item in bulkItems:
                if "New Flipper" in roles or "Intermediate Flipper" in roles or "Experienced Flipper" in roles or "Expert Flipper" in roles or "Trial Rank" in roles or "Probation" in roles or context.message.author.id == 287535385251414017:
                    if context.message.channel.id != 465893365330739220:
                        await context.send("{} Reports for **{}** should go in {}".format(context.message.author.mention, item, client.get_guild(465889718349856779).get_channel(465896763530805248).mention))
                        await context.message.delete()
                    else:
                        await ReportItem(context, item, args)
            elif item in experiencedItems:
                if "Experienced Flipper" in roles or "Trial Rank" in roles or "Expert Flipper" in roles or context.message.author.id == 287535385251414017:
                    if context.message.channel.id != 465896763530805248:
                        await context.send("{} Reports for **{}** should go in {}".format(context.message.author.mention, item, client.get_guild(465889718349856779).get_channel(521417285395677184).mention))
                        await context.message.delete()
                    else:
                        await ReportItem(context, item, args)
                else:
                    if ReportCount[context.message.author.name] > 75:
                        await context.send("You need at least the **Experienced Flipper** rank to post reports for **{}**.\nYou meet the requirements to obtain a Trial Status! For more info see {}.".format(item, client.get_guild(465889718349856779).get_channel(465909830620676118).mention))
                    else:
                        await context.send("You need at least the **Experienced Flipper** rank to post reports for **{}**.\nFor more information on ranks and their requirements see {}.".format(item, client.get_guild(465889718349856779).get_channel(465909830620676118).mention))
            elif item in intermediateItems:
                if "Intermediate Flipper" in roles or "Experienced Flipper" in roles or "Trial Rank" in roles or "Expert Flipper" in roles or"Expert Flipper" in roles or context.message.author.id == 287535385251414017:
                    if context.message.channel.id != 561290453945810954:
                        await context.send("{} Reports for **{}** should go in {}".format(context.message.author.mention, item, client.get_guild(465889718349856779).get_channel(561290453945810954).mention))
                        await context.message.delete()
                    else:
                        await ReportItem(context, item, args)
                else:
                    await context.send("You need at least the **Intermediate Flipper** rank to post adjustments for **{}**.\nFor more information on ranks and their requirements see {}.".format(item, client.get_guild(465889718349856779).get_channel(465909830620676118).mention))

    else:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('TGEJson.json', scope)
        gc = gspread.authorize(credentials)
        workSheet = gc.open("CurrentReportList").worksheet("Items")
        newFlipperItems = workSheet.col_values(3)[1:]
        intermediateItems = workSheet.col_values(6)[1:]
        experiencedItems = workSheet.col_values(9)[1:]
        bulkItems = workSheet.col_values(12)[1:]
        allItems = newFlipperItems + intermediateItems + experiencedItems + bulkItems

        roles = []
        member = client.get_guild(465889718349856779).get_member(context.message.author.id)
        for role in member.roles:
            roles.append(role.name)

        item = args[0]
        if item in allItems:
            if item in newFlipperItems or item in bulkItems:
                if "New Flipper" in roles or "Intermediate Flipper" in roles or "Experienced Flipper" in roles or "Expert Flipper" in roles or "Trial Rank" in roles or "Probation" in roles:
                    await ReportItem(context, item, args)
                else:
                    await context.send("You need at least the **New Flipper** rank to post reports for **{}**.\nYou can ask for this role from any moderator/staff member".format(item))

            elif item in experiencedItems:
                if "Experienced Flipper" in roles or "Trial Rank" in roles or "Expert Flipper" in roles or context.message.author.id == 287535385251414017:
                    await ReportItem(context, item, args)
                else:
                    if ReportCount[context.message.author.name] > 75:
                        await context.send("You need at least the **Experienced Flipper** rank to post reports for **{}**.\nYou meet the requirements to obtain a Trial Status! For more info see {}.".format(item, client.get_guild(465889718349856779).get_channel(503555214578679818).mention))
                    else:
                        await context.send("You need at least the **Experienced Flipper** rank to post reports for **{}**.\nFor more information on ranks and their requirements see {}.".format(item, client.get_guild(465889718349856779).get_channel(503555214578679818).mention))
            elif item in intermediateItems:
                if "Intermediate Flipper" in roles or "Experienced Flipper" in roles or "Trial Rank" in roles or "Expert Flipper" in roles or"Expert Flipper" in roles or context.message.author.id == 287535385251414017:
                    await ReportItem(context, item, args)
                else:
                    await context.send("You need at least the **Intermediate Flipper** rank to subscribe to **{}**.\nFor more information on ranks and their requirements see {}.".format(item, client.get_guild(465889718349856779).get_channel(465909830620676118).mention))
        else:
            context.send("We don't cover **{}**. Let Jayleno know if this is wrong!".format(item))

@client.command(pass_context=True, aliases=["UNSUBSCRIBE", "unsubscribe", "US", "us"])
async def Unsubscribe(context, *args):
    if args[0].upper() == "ALL":
        for players in NotificationTable.values():
            if context.message.author.id in players:
                players.remove(context.message.author.id)
        await context.send("You have been unsubscribed from all items")
    for item in args:

        if item.endswith(","):
            item = item[:-1]

        if item in NotificationTable:
            players = NotificationTable[item]
            players.remove(context.message.author.id)
            await context.send("You have been unsubscribed from **{}**".format(item))
    with open("NotificationTableBig.txt", "wb") as out_file:
        pickle.dump(NotificationTable, out_file)

@client.command(pass_context=True, aliases=["MYSUBS", "mysubs", "M", "m"])
async def MySubs(context, *args):
    items = []

    for item in NotificationTable.keys():
        if context.message.author.id in NotificationTable[item]:
            items.append(item)

    mess = ", ".join(items[:])
    if items == []:
        await context.send("You are not subscribed to any items")
    else:
        await context.send("You are subscribed to: {}".format(mess))

@client.command(pass_context=True, aliases=["HISTORY", "history", "H", "h"])
async def History(context, *args):
    if context.message.channel == context.message.author.dm_channel:
        await client.get_channel(466614086340313088).send(content="PM history call by: " + context.message.author.name + " for item: " + args[0])

    if context.message.channel != context.message.author.dm_channel:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('TGEJson.json', scope)
        gc = gspread.authorize(credentials)
        workSheet = gc.open("CurrentReportList").worksheet("Items")
        newFlipperItems = workSheet.col_values(3)[1:]
        intermediateItems = workSheet.col_values(6)[1:]
        experiencedItems = workSheet.col_values(9)[1:]
        bulkItems = workSheet.col_values(12)[1:]
        allItems = newFlipperItems + intermediateItems + experiencedItems + bulkItems

        roles = []
        member = client.get_guild(465889718349856779).get_member(context.message.author.id)
        for role in member.roles:
            roles.append(role.name)

        item = args[0]
        if item in allItems:
            if item in newFlipperItems:
                if "New Flipper" in roles or "Intermediate Flipper" in roles or "Experienced Flipper" in roles or "Expert Flipper" in roles or "Trial Rank" in roles or "Probation" in roles:
                    if context.message.channel.id != 465988062611243008:
                        await context.send("{} History calls for **{}** should go in {}".format(context.message.author.mention, item, client.get_guild(465889718349856779).get_channel(465988062611243008).mention))
                        await context.message.delete()
                    else:
                        await CallHistory(context, item)
                else:
                    await context.send("You need at least the **New Flipper** rank to see the history of **{}**.\nYou can ask for this role from any moderator/staff member".format(item))
            elif item in bulkItems:
                if "New Flipper" in roles or "Intermediate Flipper" in roles or "Experienced Flipper" in roles or "Expert Flipper" in roles or "Trial Rank" in roles or "Probation" in roles:
                    if context.message.channel.id != 465988062611243008:
                        await context.send("{} History calls for **{}** should go in {}".format(context.message.author.mention, item, client.get_guild(465889718349856779).get_channel(465988062611243008).mention))
                        await context.message.delete()
                    else:
                        await CallHistory(context, item)
            elif item in experiencedItems:
                if "Experienced Flipper" in roles or "Trial Rank" in roles or "Expert Flipper" in roles or context.message.author.id == 287535385251414017:
                    if context.message.channel.id != 535522244630151169:
                        await context.send("{} History calls for **{}** should go in {}".format(context.message.author.mention, item, client.get_guild(465889718349856779).get_channel(535522244630151169).mention))
                        await context.message.delete()
                    else:
                        await CallHistory(context, item)
                else:
                    if ReportCount[context.message.author.name] > 75:
                        await context.send("You need at least the **Experienced Flipper** rank to see the history of **{}**.\nYou meet the requirements to obtain a Trial Status! For more info see {}.".format(item, client.get_guild(465889718349856779).get_channel(465909830620676118).mention))
                    else:
                        await context.send("You need at least the **Experienced Flipper** rank to see the history of **{}**.\nFor more information on ranks and their requirements see {}.".format(item, client.get_guild(465889718349856779).get_channel(465909830620676118).mention))
            elif item in intermediateItems:
                if "Intermediate Flipper" in roles or "Experienced Flipper" in roles or "Trial Rank" in roles or "Expert Flipper" in roles or"Expert Flipper" in roles or context.message.author.id == 287535385251414017:
                    if context.message.channel.id != 561290832439803937:
                        await context.send("{} History calls for **{}** should go in {}".format(context.message.author.mention, item, client.get_guild(465889718349856779).get_channel(561290832439803937).mention))
                        await context.message.delete()
                    else:
                        await CallHistory(context, item)
                else:
                    await context.send("You need at least the **Intermediate Flipper** rank to post adjustments for **{}**.\nFor more information on ranks and their requirements see {}.".format(item, client.get_guild(465889718349856779).get_channel(465909830620676118).mention))

    else:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('TGEJson.json', scope)
        gc = gspread.authorize(credentials)
        workSheet = gc.open("CurrentReportList").worksheet("Items")
        newFlipperItems = workSheet.col_values(3)[1:]
        intermediateItems = workSheet.col_values(6)[1:]
        experiencedItems = workSheet.col_values(9)[1:]
        bulkItems = workSheet.col_values(12)[1:]
        allItems = newFlipperItems + intermediateItems + experiencedItems + bulkItems

        roles = []
        member = client.get_guild(465889718349856779).get_member(context.message.author.id)
        for role in member.roles:
            roles.append(role.name)

        item = args[0]
        if item in allItems:
            if item in newFlipperItems or item in bulkItems:
                if "New Flipper" in roles or "Intermediate Flipper" in roles or "Experienced Flipper" in roles or "Expert Flipper" in roles or "Trial Rank" in roles or "Probation" in roles:
                    await CallHistory(context, item)
                else:
                    await context.send("You need at least the **New Flipper** rank to see the history of **{}**.\nYou can ask for this role from any moderator/staff member".format(item))

            elif item in experiencedItems:
                if "Experienced Flipper" in roles or "Trial Rank" in roles or "Expert Flipper" in roles or context.message.author.id == 287535385251414017:
                    await CallHistory(context, item)
                else:
                    if ReportCount[context.message.author.name] > 75:
                        await context.send("You need at least the **Experienced Flipper** rank to see the history of **{}**.\nYou meet the requirements to obtain a Trial Status! For more info see {}.".format(item, client.get_guild(465889718349856779).get_channel(465909830620676118).mention))
                    else:
                        await context.send("You need at least the **Experienced Flipper** rank to see the history of **{}**.\nFor more information on ranks and their requirements see {}.".format(item, client.get_guild(465889718349856779).get_channel(465909830620676118).mention))
            elif item in intermediateItems:
                if "Intermediate Flipper" in roles or "Experienced Flipper" in roles or "Trial Rank" in roles or "Expert Flipper" in roles or"Expert Flipper" in roles or context.message.author.id == 287535385251414017:
                    await CallHistory(context, item)
                else:
                    await context.send("You need at least the **Intermediate Flipper** rank to subscribe to **{}**.\nFor more information on ranks and their requirements see {}.".format(item, client.get_guild(465889718349856779).get_channel(465909830620676118).mention))
        else:
            context.send("We don't cover **{}**. Let Jayleno know if this is wrong!".format(item))


@client.event
async def on_message(message):

    args = message.content.split(" ")

    global NotificationTable

    if message.author.id == 172337831824457728:
        if random.randint(0, 100) > 99:
            emoji = get(client.emojis, name='leila')
            await message.add_reaction(emoji)
            return

    if ":leila:" in message.content:
        if message.author.id == 172337831824457728 and random.randint(0, 100) > 95:
            await message.channel.send_message("You really enjoy this way too much, don't you <@172337831824457728>?")
        emoji = get(client.emojis, name='leila')
        await message.add_reaction(emoji)

    if args[0].upper() == "!HELP" or args[0].upper() == "!COMMANDS":

        text = "These are the commands for the FlipBot: \nAnywhere it says [item] you should replace it with the item you are refering to (like: !subscribe swh)\n\n'!subscribe [item]' *alias: '!s'* -> Adds you to the notification list for item[item]\n'!unsubscribe [item]' *alias '!us'* -> Removes you from the notification list for item [item]\n'!unsubscribe all' -> Removes you from all notification lists\n'!mysubs' *alias '!m'* -> Shows which items you are subscribed to\n'!notify [item] [message]' *alias '!n'* -> Notifies everyone that is subscribed to item[item] and also sends them a message:\nUsage: '!notify swh nib 96.9' -> Notifies the following message: You have been notified for the item: swh by [caller of the command]: nib 96.9 at: [UTC time when the notify was sent]'\n\n'!commands' *alias '!help'* -> sends this message!"
        try:
            await message.author.dm_channel.send_message(text)
        except:
            await message.channel.send_message("You have disabled pm")
            print("%s has disabled pms!" % (message.author))

    if args[0].upper() == "!ADJUSTSILENCE":
        if message.author.id in AdjustSilence:
            AdjustSilence.remove(message.author.id)
            await message.channel.send_message("You will get adjustment notifications again")
            with open("AdjustSilenceListBig", "wb") as f:
                pickle.dump(AdjustSilence, f)
        else:
            AdjustSilence.append(message.author.id)
            await message.channel.send_message("You will not get adjustment notifications untill this command is called again.")
            with open("AdjustSilenceListBig", "wb") as f:
                pickle.dump(AdjustSilence, f)

    if args[0].upper() == "!SILENCE":
        if message.author.id in Silence:
            Silence.remove(message.author.id)
            await message.channel.send_message("You will get notifications again")
            with open("SilenceListBig", "wb") as f:
                pickle.dump(Silence, f)
        else:
            Silence.append(message.author.id)
            await message.channel.send_message("You will not get notifications again untill this command is called again.")
            with open("SilenceListBig", "wb") as f:
                pickle.dump(Silence, f)
    if args[0].upper() == "@NOTIFYWEEBS":
        await message.channel.send(content="<@272447772777512960>")

    roles = []

    if message.guild == client.get_guild(465889718349856779):
        for role in message.author.roles:
            roles.append(role.name)


    if "TGE Staff" in roles or "Moderator" in roles:

        if args[0].upper() == "STARTACHIEVEMENTS":
            chnl = client.get_channel(522232855359651850)
            for ach in AchievementsBatch2:
                await chnl.send(file="TGEAchievements/" + ach)
                await chnl.send_message("Obtained by:")
            done = await chnl.send_message("Finished!")
            time.sleep(5)
            await done.delete()

        if args[0].upper() == "CLEARSUBS":
            NotificationTable = dict.fromkeys({})
            print("Subs Cleared")
            with open("NotificationTableBig.txt", "wb") as out_file:
                pickle.dump(NotificationTable, out_file)


        if args[0].upper() == "ACHIEVEMENTGET":
            msgid = args[1]
            msg = await client.get_channel(522232855359651850).fetch_message(msgid)
            msgcontent = msg.content
            user = args[2]
            msgcontent += "\n - " + user + " " + str(message.created_at.date())
            try:
                await msg.edit(msgcontent)
            except:
                await message.channel.send("Achievements full! Do more lines!")

        if args[0].upper() == "MORELINES":
            msgid = args[1]
            msg = await client.get_channel(522232855359651850).fetch_message(msgid)
            msgcontent = msg.content
            chnl = client.get_channel(522232855359651850)
            await chnl.send(file="TGEAchievements/" + args[2] + ".png")
            await chnl.send(msgcontent)
            user = args[3]
            await chnl.send(" - " + user + " " + str(message.created_at.date()))

        if args[0].upper() == "GETCOUNT":
            mess = str(message.created_at.date()) + "\n\n **Reports: ** \n"

            if len(args) > 1:
                if args[1].upper() == "AMOUNT":
                    s = [(k, ReportCount[k]) for k in sorted(ReportCount, key=ReportCount.get, reverse=True)]
                    for k, v in s:
                        mess += "{0}: {1} \n".format(k, v)
                    await message.channel.send(mess)
                    mess = "**History Calls: ** \n"

                    s = [(k, HistoryCount[k]) for k in sorted(HistoryCount, key=HistoryCount.get, reverse=True)]
                    for k, v in s:
                        mess+= "{0}: {1} \n".format(k, v)
                    await message.channel.send(mess)

                else:
                    user = " ".join(args[1:])
                    if user in ReportCount:
                        mess += user + ": " + str(ReportCount[user]) + "\n\n"
                        mess += "**History Calls: ** \n"
                        mess += user + ": " + str(HistoryCount[user]) if user in HistoryCount else "None"
                        await message.channel.send(mess)
                    else:
                        await message.channel.send("User '" + user + "' not found.")

            else:
                for k, v in sorted(ReportCount.items()):
                    mess += "{0}: {1} \n".format(k, v)
                await message.channel.send(content=mess)
                mess = "**History Calls: ** \n"

                for k, v in sorted(HistoryCount.items()):
                    mess+= "{0}: {1} \n".format(k, v)
                await message.channel.send(content=mess)

        if args[0].upper() == "REPORTSTODAY":
            await message.channel.send(str(DailyReports))

        if args[0].upper() == "!PRINTLIST":
            for k, v in ItemList.items():
                print(k + " - " + v + "\n")

        if args[0].upper() == "TESTREMOVE" and 1==1:


            members = []
            for server in client.guilds:
                if server.id == 367329784344346637:
                    for member in server.members:
                        members.append("!" + member.id)
                        members.append(member.id)

            notificationmembers = []
            for item in NotificationTable:
                for player in NotificationTable[item]:
                    if player not in notificationmembers:
                        notificationmembers.append(player)
                        user = await client.get_user(player)

            for member in notificationmembers:
                if member not in members:
                    removables = dict.fromkeys(firstItems)
                    for item in NotificationTable:
                        for player in NotificationTable[item]:
                            if player == member:
                                user = await client.get_user(member)
                                if player in removables:
                                    removables[player].append(item)
                                else:
                                    itemlist = []
                                    itemlist.append(item)
                                    removables[player] = itemlist
                    print(removables)
                    for k, v in removables.items():
                        print("{0}: {1} \n".format(k, v))
                        for item in v:
                            NotificationTable[item].remove(k)
            print("Done!")
    await client.process_commands(message)

Loop.start()
client.run("BOT_KEY_HERE")

