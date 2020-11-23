###########################################################################################################
#                         Twitch Clip Downloader script by David Simmerson (SimmyDizzle)                  #
###########################################################################################################
# This system will download twitch clips from a specified streamer and will continue to check back on a   #
# timer and download the latest and greatest from said streamer. This is designed to allow for multiple   #
# attempts, over, and over again. This will be used to continue to check, with default values.            #
# By default this will query every 5 minutes.                                                             #
# This also links to a webhook for Discord to post links to the twitch clip directly into the discord     #
# with a proper embed.                                                                                    #
# More options possibly coming soon-ish, once it is properly tested and proven working.                   #
###########################################################################################################
# Discord:   https://discord.gg/T4vrfVy                                                                   #
# Stream:    https://twitch.tv/SimmyDizzle                                                                #
# Twitter:   https://twitter.com/LiveSimmy                                                                #
# Instagram: https://instagram.com/LiveSimmy                                                              #
# Facebook:  https://facebook.com/LiveSimmy                                                               #
###########################################################################################################
# Twitch Kraken API:    https://dev.twitch.tv/docs/v5                (deprecated)                         #
# Twitch API Reference: https://dev.twitch.tv/docs/api/reference                                          #
###########################################################################################################


#import our required systems
###########################################################################################################
# Note:  pip install requests
#        pip install twitchAPI
#        pip install discord-webhook
#        otherwise this will not function.
import requests, os, time, sys, json, shutil, urllib

###########################################################################################################
# import our discord data
from discord_webhook import DiscordWebhook, DiscordEmbed
  
# This is required for all modern twitch pulls. Some of the API may work, however it looks like I may have
# to replace the kraken pulls with a modern twitch pull. If the V5 kraken pulls still work, we will leave it
# as is and develop further as required. However it appears that this may no longer be viable.
# this is required moving forward for modern API.
from twitchAPI.twitch import Twitch

# get the datetime
from datetime import datetime

###########################################################################################################
# Our Discord WebHook URL
# Webhooks allow us to post this data into our Discord chat automatically, which is pretty frikken stellar.
# so we will put our webhook here.
Webhook = ""

# This will be used in your 'footer' and will be assigned to your post title url.
Discord_Icon_Url = ""

#set the default NitroStatus to False.  This will be read in from the config later.
NitroStatus = False

# Identify the folder to write our files to.
Folder = ""

###########################################################################################################
# Name the streamer to monitor
Streamer = ""

# How far back to check in the archive of clips to download
Period_To_Check = "day"

# Total amount of clips to download in one pass. (at 5 minute intervals, clips should not exceed 10, or really, 2)
Clips_To_Download = 10

# Time till next query in seconds
Clip_Query_Timer = 300 # 300 seconds = 5 minutes

# block certain characters from being within the request (we will just strip them later on when I have time to write it)
invalid_chars = ["?", "\\", "/", "*", ":", "<", ">", "|", '"']

###########################################################################################################
LOG_MODE = True
PRINT_LOG = True

###########################################################################################################
# our twitch creds are empty, we load from file, but we initiate an empty data here
# because sometimes people need to see things to understand them. (Me included)
globalTwitch_Creds = ''
Twitch_Secret = ''
Twitch_ID = ''
Twitch_Access_Token = ''
Twitch_Headers = ''

def Timestamp():
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")

    return timestampStr

###########################################################################################################
## Function: WriteLog
## Arguments: string
##
## example: WriteLog(f"Some data {data}")
def WriteLog(str):
    # write the log to the flat-file
    if LOG_MODE == True:
        log_dir = f"{os.path.dirname(os.path.realpath(__file__))}/logs"

        # make sure our log-directory exists!
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)

        date = datetime.now()
        pathN = date.strftime("%d-%b_%Y")

        logF = open(f"{log_dir}/log_{pathN}.txt", "a")
        logF.write(f"{Timestamp()}: {str}\n")
        logF.close()

    # write the log to the console?
    if PRINT_LOG == True:
        print(f"{Timestamp()}: {str}")
    

###########################################################################################################
## Function: Reconnect
## Arguments: none
##
## This will connect and download the twitch token again, which expires, so this is vital to reconnect every
## now and then to ensure we do not expire. Based on 5 minute intervals, 
def Reconnect():
    Get_Twitch_Token()
    global Twitch_Headers

    # build our globally used header (multitasking at its best)
    Twitch_Headers = {"Client-ID": Twitch_ID, "Authorization": "Bearer " + Twitch_Access_Token}

    ts = Timestamp()

    WriteLog (f"{Twitch_Headers}")


###########################################################################################################
## Function: Main
## Arguments: none
##
def Main():
    GoneOffline = False
    WasOnline = False

    loopCount = 0

    WriteLog ("We will now loop till death!")
    # We loop till someone forcably closes us. Because we want to live forever!
    while True:
        loopCount = loopCount +1
        ts = Timestamp()
        
        ##################################################################################################
        # tell the system to reconnect and get our new token
        # should prevent our script from timing out.
        if loopCount == 12: # 12 will be 1hr in 5 minute intervals (math), this will be longer when not live.
            Reconnect()
            loopCount = 0
            WriteLog(f"Reconnected to {Streamer} from client ID: {Twitch_ID}.")
        
        if GoneOffline:
            WriteLog(f"According to our last check, {Streamer}, has gone offline.")
	
	#Is the streamer online (will return 1 if true)
        if Check_User_Online(Streamer) == 1:
        #if 1 == 1:
            if GoneOffline:
                WriteLog(f"{Streamer} is back online! Suspect connection hiccup.")
            else:
                WriteLog(f"{Streamer} is online, checking for new clips!")
                
            WasOnline = True
            Download_Clips(Clips_To_Download)
            GoneOffline = False
	    
	    #this would be a 5 minute timer.
            time.sleep(Clip_Query_Timer)
        else:
	    # we don't care what other response we got, stream is offline
	    # or not existent user. But we digress, we will use our other
	    # checks to verify what is going on.
            if WasOnline:
                WriteLog(f"{Streamer} has gone offline currently.")
                Download_Clips(Clips_To_Download)
                GoneOffline = True
                WasOnline = False
		# this would be a 10 minute timer
                time.sleep(Clip_Query_Timer * 2)
            else:
		# we were not online, we completely reset data, and wait a long time
		# this is because we don't want to spam twitch with needless queries
		# so we simply change out our state.
                WasOnline = False
                GoneOffline = False
                WriteLog(f"{Streamer} is currently offline.")
		# this would be a 25 minute timer
                time.sleep(Clip_Query_Timer * 5)
	
###########################################################################################################
## Function: Read_Twitch_Config
## Arguments: none
def Read_Twitch_Config():
    global Twitch_ID
    global Twitch_Secret
    global Webhook
    global Discord_Icon_Url
    global Streamer
    global Folder
    global NitroStatus
    
    configFile = open("Config.txt")
    for line in configFile:
        if line.startswith("Client_ID:"):
            Twitch_ID = line[line.index(":")+1:].strip()
            WriteLog(f"Client ID: {Twitch_ID}")
        elif line.startswith("Client_Secret:"):
            Twitch_Secret = line[line.index(":")+1:].strip()
            WriteLog(f"Client Secret: {Twitch_Secret}")
        elif line.startswith("Webhook:"):
            Webhook = line[line.index(":")+1:].strip()
            WriteLog(f"Webhook: {Webhook}")
        elif line.startswith("Discord_Icon_Url:"):
            Discord_Icon_Url = line[line.index(":")+1:].strip()
            WriteLog(f"Discord_Icon_Url: {Discord_Icon_Url}")
        elif line.startswith("Streamer:"):
            Streamer = line[line.index(":")+1:].strip()
            WriteLog(f"Streamer: {Streamer}")
        elif line.startswith("Folder:"):
            Folder = line[line.index(":")+1:].strip()
            WriteLog(f"Folder: {Folder}")
        elif line.startswith("Nitro:"):
            strToView = line[line.index(":")+1:].strip()
            if strToView == 'true':
                NitroStatus = True
            else:
                NitroStatus = False
            WriteLog(f"NitroStatus: {NitroStatus}")
        elif line.startswith("#"):
            # do nothing
            doNothing = True #this is here to just stop stupid warnings for now.
        else:
            WriteLog(f"Unknown field in Config.txt: {line}")
            

    # Make sure our directory is created.
    if not os.path.exists(Folder):
        os.mkdir(Folder)

    configFile.close()

###########################################################################################################
## Function: Get_Twitch_Token
## Arguments: none
##
## This is required to populate use the new API, we need our access token
##
def Get_Twitch_Token():
    global Twitch_ID
    global Twitch_Secret
    global Twitch_Access_Token
    autURL = "https://id.twitch.tv/oauth2/token"
    autParams={"client_id": Twitch_ID, "client_secret": Twitch_Secret, "grant_type": "client_credentials"}
    autCall = requests.post(url=autURL, params=autParams)
    autData=autCall.json()
    Twitch_Access_Token = autData["access_token"]

	
###########################################################################################################
## Function: Check_User_Online
## Arguments: none
##
def Check_User_Online(user):

    # Okay, build the stream URL path
    streamsURL = "https://api.twitch.tv/helix/streams"

    # our parameters, we just need our streamer name.
    params = {"user_login": f"{Streamer}"} #used to pass the username to the API call

    # lets connect to twitch and find out if the stream is live!
    StreamerJSon = requests.get(url=streamsURL, headers=Twitch_Headers, params=params).json()
    stream = StreamerJSon.get('data') 

    try:
	# Identify if we are live or not.
        if stream[0]['type'] == 'live':
            status = 1
        else:
            status = 0
    except: #there is no data, and therefore the streamer is not live
        status = 0

    # return our status because science
    return status
	
###########################################################################################################
## Function: Download_Clips
## Arguments: total amount of clips
##
def Download_Clips(total_clips):
    global NitroStatus
    
    dl_headers = {'Accept':"application/vnd.twitchtv.v5+json", 'Client-ID': Twitch_ID}

    # Initialize our clips to 0
    Clips = []

    #kraken API (v5) may no longer work. We will check fully on Monday and adjust accordingly.
    response = requests.get("https://api.twitch.tv/kraken/clips/top", params = {"channel": Streamer, "trending": "false", "period": Period_To_Check, "limit": total_clips, "language": "en"}, headers=dl_headers).json()
    Clips.append(response)

    for json_holder in Clips:
        for json_data in json_holder["clips"]:
        
            ###########################################################################################################
            #Thanks to @CommanderRoot for the quick references to help set this up. (https://twitter.com/CommanderRoot/status/1326963131134996482?s=20)
            #Twitch API Guide:  https://dev.twitch.tv/docs/api/reference#get-clips
            #This is why I @ people on twitter, this was a huge help for setting this up.

            #This is *PURE* debugging, when looking at the json data
            #print (json)

            title = ''.join(i for i in json_data["title"] if i not in invalid_chars)
            slug = ''.join(i for i in json_data["slug"] if i not in invalid_chars)
            Category = json_data["game"]
            Channel = ''.join(i for i in json_data["broadcaster"]["display_name"] if i not in invalid_chars)
            created_at = json_data["created_at"]
            #for use in the discord integration (webhook w/embeds)
            preview_url = json_data["thumbnails"]["medium"]

            #this pythonic enough?
            vod_url = json_data["vod"]["preview_image_url"].replace('-preview.jpg', '.mp4')

            # Identify the file-to save.
            Filename = f"{Folder}/{slug}.mp4"
            if not os.path.exists(Filename):
                
                # grab the download link from twitch and retrieve the file.
                response = requests.get(vod_url)

		# write binary file
                with open(Filename, 'wb') as fd:
                    for chunk in response.iter_content(chunk_size=100000):
                        fd.write(chunk)

                # debugging purposes, identify the title downloaded.
                WriteLog(f"Downloaded: {slug}.mp4")


                ###########################################################################################################
                ## Discord integration
                if Webhook:
                    data = {}

                    wh = DiscordWebhook(url=Webhook)

                    embed = DiscordEmbed(title=f"Clip: {slug}", description=f"Content: {Category}\n\r [Clip here on Twitch](https://clips.twitch.tv/{slug})", color=242424)

                    embed.set_author(name=f"{Streamer}", url=f"https://www.twitch.tv/{Streamer}", icon_url=f"{Discord_Icon_Url}")

                    embed.set_thumbnail(url=f"{preview_url}")
                    embed.set_timestamp()


                    ################################################################
                    # attempt a work-around for twitch, as they convert : instead of dropping them like a normal website would.
                    catAttempt = f"{Category}"

                    # add fields to embed
                    catFix = urllib.parse.quote(f"{catAttempt}")

                    #not quite yet, TODO: Fix this, it does not turn : into %3A, must ensure all values are properly converted
                    #so that twitch will recognize the game properly when linked, but it is coming.
                    print(f"catFix: {catFix}")
                    
                    embed.add_embed_field(name='Game', value=f"[{Category}](https://www.twitch.tv/directory/game/{catFix})")
                    embed.add_embed_field(name='Channel', value=f'[{Streamer}](https://www.twitch.tv/{Streamer})')

                    #if NitroStatus == True:
                    # Here we will attempt to FFMPEG the file to a smaller file size
                    # as to allow us to upload the video, however Discord has file size restraints
                    # that we must account for first.
                    # The max webhook size is 8mb: https://discord.com/developers/docs/resources/channel#create-message
                    # so this will not be 'fool proof' unless discord increases the limits from 8mb.
                    # so we will attempt to upload the file, if we are successful, great, if-not, we will push the
                    # link to the clip URL.
                    #    with open(f"{Filename}", "rb") as f:
                    #        wh.add_file(file=f.read(), filename=f"{slug}.mp4")
                    #else:
                    embed.set_image(url=f"{preview_url}")
                    #embed.set_video(url=f"{vod_url}")

                    embed.set_footer(text=f"This post was automatically grabbed from twitch and posted. Bot Life.\n\r")

                    #attempt to post our embeded file.
                    wh.add_embed(embed)
                    response = wh.execute()
                    
                    #now we check the response code and see if the file was too large.
                    #if it is too large, we will just attach it the old fashioned way.
                    #nitro servers can have up to 100mb uploads.
                    #at level 3. Base file size maxes out at 2mb, level 1, at 8mb. etc.
                    
                    #this is still to be done, as it stands I have no means to test if this
                    #will work on larger servers, so I have left it out for the moment.


                else:
                    # Debugging purposes
                    WriteLog("Discord Webhooks not currently installed.")
            ###########################################################################################################
            ## Path already exists? Means we got the file already, ignore it. (for now we log that we got it for testing)
            ## Not required unless debugging.
            else: 
                # For debugging purposes, we leave this here.
                WriteLog(f"Already Downloaded: {slug}.mp4")

    # Cleanup our list of clips.
    Clips = []

###########################################################################################################
## Ensure we have our twitch_creds.dat file (required for twitch api)
## visit Twitch API Client ID: https://dev.twitch.tv/console/apps/create 
## to create an app and use the code here.
##
## This reads in our credentials from a flat-file. This is required for the new non-kraken based API.
Read_Twitch_Config()

###########################################################################################################
## Now that we got the data out of the config file, we will attempt to get our token. This will grant us
## access to the API properly, and we will be able to work accordingly.
Reconnect()

###########################################################################################################
## --- Instantiate the main function and begin our forever loop (5 minutes between each check against twitch)
Main()


## EOF
