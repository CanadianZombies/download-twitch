[![Stars](https://img.shields.io/github/stars/canadianzombies/download-twitch.svg?style=plastic)](https://github.com/canadianzombies/download-twitch/stargazers)
[![Issues](https://img.shields.io/github/issues/canadianzombies/download-twitch?style=plastic)](https://github.com/canadianzombies/download-twitch/issues)
[![Size](https://img.shields.io/github/repo-size/canadianzombies/download-twitch.svg?style=plastic)](https://github.com/canadianzombies/download-twitch)
[![Discord](https://img.shields.io/discord/234145231359049729?style=plastic)](https://discord.gg/bCsV7km9PE)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg?style=plastic)](https://github.com/psf/black)
[![Donate PayPal](https://img.shields.io/badge/donate-paypal-blue.svg?style=plastic)](https://www.paypal.me/simmydizzle)

#######################################################################################
# download-twitch
Here we are, downloading twitch clips, and embedding into discord.

This system utilizes twitch, downloads the clips from a specified streamer on a timer. 

This will, if configured properly, embed links to clip into your discord. Allowing you to
have a whole new level of engagement. This is super important to get into your community.

#######################################################################################
This system has now been tested (November 15 2020) and is working. 

It still uses some Kraken API, but it works, I will eventually move this entirely to Helix.

This is pretty straightforward, but if you need help setting it up, please contact me on Twitter: @livesimmy

I will do my best to help people configure this for their streams.

#######################################################################################
# Requirements
Please use pip to install the following systems
pip install requests
pip install twitchAPI
pip install discord-webhook

These are required to connect to twitch and discord.

#######################################################################################
# Twitch App
To create a new app and get your twitch client ID and secret, go here https://dev.twitch.tv/console/apps/create

Fill out the data, set the URL to localhost

Then have it re-generate your secret and copy it.

#######################################################################################
# Config.txt
Create Config.txt in the same directory as your twitch.py.
Put this in the file.

Client_ID: Your Client ID here

Client_Secret: Your Client Secret here


# Instructions

Fill out the Config.txt, it is pretty self explanitory. If you need help, hit me up on twitter @LiveSimmy and I will help as I can.

