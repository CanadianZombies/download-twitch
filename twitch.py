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

# This will be used in your 'footer' and will be assigned to your post title url.
Discord_Icon_Url = ""

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

###########################################################################################################
# our twitch creds are empty, we load from file, but we initiate an empty data here
# because sometimes people need to see things to understand them. (Me included)
globalTwitch_Creds = ''
Twitch_Secret = ''
Twitch_ID = ''
Twitch_Access_Token = ''
Twitch_Headers = ''

###########################################################################################################
## Function: Main
## Arguments: none
##
def Main():
    GoneOffline = False
    WasOnline = False


    print ("We will now loop till death!")
    # We loop till someone forcably closes us. Because we want to live forever!
    while True:
        if GoneOffline:
            print(f"According to our last check, {Streamer}, has gone offline.")
	
	#Is the streamer online (will return 1 if true)
        if Check_User_Online(Streamer) == 1:
            if GoneOffline:
                print(f"{Streamer} is back online! Suspect connection hiccup.")
            else:
                print(f"{Streamer} is online, checking for new clips!")
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
                print(f"{Streamer} has gone offline currently.")
                Download_Clips(Clips_To_Download, Period_To_Check)
                GoneOffline = true
                WasOnline = False
		# this would be a 10 minute timer
                time.sleep(Clip_Query_Timer * 2)
            else:
		# we were not online, we completely reset data, and wait a long time
		# this is because we don't want to spam twitch with needless queries
		# so we simply change out our state.
                WasOnline = False
                GoneOffline = False
                print(f"{Streamer} is currently offline.")
		# this would be a 25 minute timer
                time.sleep(Clip_Query_Timer * 5)
	
###########################################################################################################
## Function: Read_Twitch_Config
## Arguments: none
def Read_Twitch_Config():
    configFile = open("Config.txt")
    for line in configFile:
        if line.startswith("Client_ID:"):
            Twitch_ID = line[line.index(":")+1:].strip()
            print(Twitch_ID)
        elif line.startswith("Client_Secret:"):
            Twitch_Secret = line[line.index(":")+1:].strip()
            print(Twitch_Secret)
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
    print (autParams)
    print (autCall)
    autData=autCall.json()
    print(autData)
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
        isLive = stream[0]['type'] == "live" 
    except: #there is no data, and therefore the streamer is not live
        isLive = False

    if isLive:
        status = 1
    else:
        status = 0

    # return our status because science
    return status
	
###########################################################################################################
## Function: Download_Clips
## Arguments: total amount of clips
##
def Download_Clips(total_clips):

    dl_headers = {'Accept':"application/vnd.twitchtv.v5+json", 'Client-ID': Twitch_ID}

    # Initialize our clips to 0
    Clips = []

    #kraken API (v5) may no longer work. We will check fully on Monday and adjust accordingly.
    response = requests.get("https://api.twitch.tv/kraken/clips/top", params = {"channel": Streamer, "trending": "false", "period": Period_To_Check, "limit": total_clips, "language": "en"}, headers=dl_headers).json()
    Clips.append(response)

    print (response)
    
    for json_holder in Clips:
        for json_data in json_holder["clips"]:
        
            ###########################################################################################################
            #Thanks to @CommanderRoot for the quick references to help set this up. (https://twitter.com/CommanderRoot/status/1326963131134996482?s=20)
            #Twitch API Guide:  https://dev.twitch.tv/docs/api/reference#get-clips
            #This is why I @ people on twitter, this was a huge help for setting this up.

            print (json)

            title = ''.join(i for i in json_data["title"] if i not in invalid_chars)
            slug = ''.join(i for i in json_data["slug"] if i not in invalid_chars)
            Category = ''.join(i for i in json_data["game"] if i not in invalid_chars)
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
                print(f"Downloaded: {slug}.mp4")


                ###########################################################################################################
                ## Discord integration
                if Webhook:
                    data = {}

                    #for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
                    data["content"] = f"The latest clip by {Streamer} @ {created_at}."
                    data["tts"] = "false"

                    data["username"] = "Cpl Bloggins"
                    data["timestamp"] = f"{created_at}"
                    data["image"] = f"{preview_url}"                    

                    #leave this out if you dont want an embed
                    data["embeds"] = []
                    embed = {}

                    #for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
                    embed["description"] = f"{Category}"
                    embed["title"] = f"{slug}"

                    embed["url"] = f"https://clips.twitch.tv/{slug}"

                    # build our dicts, because, science.
                    embed["author"] = {}
                    embed["thumbnail"] = {}
                    embed["image"] = {}
                    embed["footer"] = {}
                    

                    author = {}
                    author["name"] = f"{Streamer}"
                    author["url"] = "https://www.twitch.tv/simmydizzle"
                    author["icon_url"] = f"{Discord_Icon_Url}"

                    footer = {}
                    footer["text"] = "This post was automatically grabbed from twitch and posted. Bot Life."
                    footer["icon_url"] = f"{Discord_Icon_Url}"

                    thumbnail = {}
                    thumbnail["url"] = f"{preview_url}"

                    image = {}
                    image["url"] = f"{preview_url}"

                    embed["author"].update(author)
                    embed["thumbnail"].update(thumbnail)
                    embed["image"].update(image)
                    embed["footer"].update(footer)



                    #  Compile our embedded data properly.
                    data["embeds"].append(embed)


                    # turn the array into proper json formated content.
                    converted_data = json.dumps(data);
                    print (converted_data)

                    # Lets connect to the webhook
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
                print(f"Already Downloaded: {slug}.mp4")

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
Get_Twitch_Token()

print(Twitch_ID)
print(Twitch_Access_Token)

# build our globally used header (multitasking at its best)`    1``
Twitch_Headers = {"Client-ID": Twitch_ID, "Authorization": "Bearer " + Twitch_Access_Token}
print (Twitch_Headers)

###########################################################################################################
## --- Instantiate the main function and begin our forever loop (5 minutes between each check against twitch)
Main()


## EOF
