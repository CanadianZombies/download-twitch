# download-twitch
Here we are, downloading twitch clips, and possibly embedding into discord.

This system utilizes twitch, downloads the clips from a specified streamer on a timer. 

Additionally, the footprint has been put in to embed into a discord the new clips.

This system has now been tested (November 15 2020) and is working. 

It still uses some Kraken API, but it works, I will eventually move this entirely to Helix.

This is pretty straightforward, but if you need help setting it up, please contact me on Twitter: @livesimmy

I will do my best to help people configure this for their streams.

# Requirements
Please use pip to install the following systems
pip install requests
pip install twitchAPI

These are required to connect to twitch and discord.

# Twitch App
To create a new app and get your twitch client ID and secret, go here https://dev.twitch.tv/console/apps/create

Fill out the data, set the URL to localhost

Then have it re-generate your secret and copy it.

# Config.txt
Create Config.txt in the same directory as your twitch.py.
Put this in the file.

Client_ID: Your Client ID here

Client_Secret: Your Client Secret here


# Configure your script

In twitch.py, in the "Webhook" variable, put in your DISCORD webhook, if you need help creating a webhook, please use google

In twitch.py, in the "Discord_Icon_Url" put a link to the picture you want to use as your icon URL.

In twitch.py, in the "Folder" variable, put the folder that you wish to use for your videos. Ex: C:/Videos

In twitch.py, in the "Streamer" variable, put the name of the streamer you want to monitor for new clips, it is defaulted to SimmyDizzle

You can configure your times for how often to check, 'period' is set to day, no need to change this.

You can also configure how many clips to download in a pass, I set it to 10, any more than that seems like overkill

You can also change how often it queries twitch. 300 is the default value, this is 5 minutes. From there we have multipliers later on to change this value accordingly.



