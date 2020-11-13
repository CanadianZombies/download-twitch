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
#        pip install twitch
#        otherwise this will not function.
import requests, os, time, sys, json

# This is required for all modern twitch pulls. Some of the API may work, however it looks like I may have
# to replace the kraken pulls with a modern twitch pull. If the V5 kraken pulls still work, we will leave it
# as is and develop further as required. However it appears that this may no longer be viable.
# this is required moving forward for modern API.
from twitchAPI.twitch import Twitch

###########################################################################################################
# Our Discord WebHook URL
# Webhooks allow us to post this data into our Discord chat automatically, which is pretty frikken stellar.
# so we will put our webhook here.
Webhook = "" # Insert the webhook URL here.

# Identify the folder to write our files to.
Folder = "C:/Users/*****/Videos/Replays/Submitted"

# Make sure our directory is created.
if not os.path.exists(Folder):
    os.mkdir(Folder)

###########################################################################################################
# Name the streamer to monitor
Streamer = "SimmyDizzle"

# How far back to check in the archive of clips to download
Period_To_Check = "day"

# Total amount of clips to download in one pass. (at 5 minute intervals, clips should not exceed 10, or really, 2)
Clips_To_Download = 10

# Time till next query in seconds
Clip_Query_Timer = 300 # 300 seconds = 5 minutes

# block certain characters from being within the request (we will just strip them later on when I have time to write it)
invalid_chars = ["?", "\\", "/", "*", ":", "<", ">", "|", '"']

# our twitch creds are empty, we load from file, but we initiate an empty data here
# because sometimes people need to see things to understand them. (Me included)
Twitch_Creds = ""

###########################################################################################################
## Function: Main
## Arguments: none
##
def Main():
    GoneOffline = false
    WasOnline = false
    # We loop till someone forcably closes us. Because we want to live forever!
    while True:
        os.system("cls")

	if GoneOffline:
	    print(f"According to our last check, {Streamer}, has gone offline.")
	
	#Is the streamer online (will return 0 if true)
	if Check_User_Online(Streamer) == 0:
	    if GoneOffline:
		print(f"{Streamer} is back online! Suspect connection hiccup.")
		
	    WasOnline = true
	    Download_Clips(Clips_To_Download, Period_To_Check)
	    GoneOffline = false
	    
	    #this would be a 5 minute timer.
            time.sleep(Clip_Query_Timer)
	else:
	    # we don't care what other response we got, stream is offline
	    # or not existent user. But we digress, we will use our other
	    # checks to verify what is going on.
	    if WasOnline:
		Download_Clips(Clips_To_Download, Period_To_Check)
		GoneOffline = true
		WasOnline = false
		# this would be a 10 minute timer
		time.sleep(Clip_Query_Timer * 2)
	    else:
		# we were not online, we completely reset data, and wait a long time
		# this is because we don't want to spam twitch with needless queries
		# so we simply change out our state.
	        WasOnline = false
		GoneOffline = false
		# this would be a 25 minute timer
		time.sleep(Clip_Query_Timer * 5)
	

###########################################################################################################
## Function: Check_User_Online
## Arguments: none
##
def Check_User_Online(user):
    # Twitch returns the following data
    # returns 0: online, 1: offline, 2: not found, 3: error """
    url = 'https://api.twitch.tv/kraken/streams/' + user
    try:
        info = json.loads(urlopen(url, timeout = 15).read().decode('utf-8'))
        if info['stream'] == None:
            status = 1
        else:
            status = 0
    except URLError as e:
        if e.reason == 'Not Found' or e.reason == 'Unprocessable Entity':
            status = 2
        else:
            status = 3
    return status
	
###########################################################################################################
## Function: Download_Clips
## Arguments: total amount of clips
##
def Download_Clips(total_clips):

    headers = {'Accept':"application/vnd.twitchtv.v5+json", 'Client-ID': Twitch_Creds}

    # Initialize our clips to 0
    Clips = []

    #kraken API (v5) may no longer work. We will check fully on Monday and adjust accordingly.
    response = requests.get("https://api.twitch.tv/kraken/clips/top", params = {"channel": Streamer, "trending": "false", "period": Period_To_Check, "limit": total_clips, "language": "en"}, headers=headers).json()
    Clips.append(response)
        
    for json_holder in Clips:
        for json in json_holder["clips"]:
        
            ###########################################################################################################
            #Thanks to @CommanderRoot for the quick references to help set this up. (https://twitter.com/CommanderRoot/status/1326963131134996482?s=20)
            #Twitch API Guide:  https://dev.twitch.tv/docs/api/reference#get-clips
            #This is why I @ people on twitter, this was a huge help for setting this up.

            title = ''.join(i for i in json["title"] if i not in invalid_chars)
            Category = ''.join(i for i in json["game"] if i not in invalid_chars)
            Channel = ''.join(i for i in json["broadcaster"]["display_name"] if i not in invalid_chars)

            #for use in the discord integration (webhook w/embeds)
            preview_url = json["vod"]["preview_image_url"]

            #this pythonic enough?
            vod_url = json["vod"]["preview_image_url"].replace('-preview.jpg', '.mp4')
            id = json["vod"]["id"]

            # Identify the file-to save.
            Filename = f"{Folder}/{id}-{Streamer}-{title}.mp4"
            if not os.path.exists(Filename):
                
                # grab the download link from twitch and retrieve the file.
                response = requests.get(vod_url)

		# write binary file
                with open(Filename, 'wb') as fd:
                    for chunk in response.iter_content(chunk_size=100000):
                        fd.write(chunk)
                
                # debugging purposes, identify the title downloaded.
                print(f"Downloaded: {id}-{Streamer}-{title}.mp4")


                ###########################################################################################################
                ## Discord integration
                if Webhook:
                    data = {}

                    #for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
                    data["content"] = "The latest clip by {Streamer}."
                    data["avatar_url"] = "https://www.canada.ca/content/dam/themes/defence/caf/militaryhistory/dhh/ranks/army-corporal.png"
                    data["username"] = "Cpl Bloggins"

                    #leave this out if you dont want an embed
                    data["embeds"] = []
                    embed = {}

                    #for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
                    embed["description"] = "{Category}"
                    embed["title"] = "{title}"
                    embed["url"] = "{vod_url}"

                    # This may not work Expect issues.
                    embed["thumbnail"]["url"] = "{preview_url}"

                    data["embeds"].append(embed)

                    # turn the array into proper json formated content.
                    converted_data = json.dumps(data);

                    result = requests.post(Webhook, converted_data, headers={"Content-Type": "application/json"})

                    try:
                        result.raise_for_status()
                    except requests.exceptions.HTTPError as discordError:
                        print(discordError)
                    else:
                        print("Discord successfully recieved the package, code {}.".format(result.status_code))
                else:
                    # Debugging purposes
                    print("Discord Webhooks not currently installed.")
            ###########################################################################################################
            ## Path already exists? Means we got the file already, ignore it. (for now we log that we got it for testing)
            else: 
                # For debugging purposes, we leave this here.
                print(f"Already Downloaded: {id}-{title}.mp4")

    # Cleanup our list of clips.
    Clips = []

###########################################################################################################
## Ensure we have our twitch_creds.dat file (required for twitch api)
## visit Twitch API Client ID: https://dev.twitch.tv/console/apps/create 
## to create an app and use the code here.
## This can be removed once the twitch_creds.dat file exists.
##
if not os.path.exists("twitch_creds.dat"):
    Twitch_Creds = input("Enter twitch client ID from dev console (For Twitch API): ")
    Twitch_Creds_File= open("twitch_creds.dat", "w+").write(ClientID)


###########################################################################################################
## --- Instantiate the main function and begin our forever loop (5 minutes between each check against twitch)
Main()


## EOF
