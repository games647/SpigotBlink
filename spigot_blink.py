#! /usr/bin/python3

from blink1.blink1 import Blink1
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import urllib
import time
import json
import struct
import configparser

# constants
USER_AGENT = 'SpigotBlink'
SPIGOT_COLOR = "ed8106"
SPIGOT_RGB = struct.unpack('BBB', bytes.fromhex(SPIGOT_COLOR))

UNREAD_ALERTS_KEY = "_visitor_alertsUnread"
UNREAD_CONVERSATION_KEY = "_visitor_conversationsUnread"

FADE_TIME = 500
# seconds
UPDATE_INTERVAL = 60


def search_updates(token, user_id):
    post_fields = {
        '_xfToken': token,
        '_xfResponseType': 'json'
    }

    request = Request('https://www.spigotmc.org/index.php?liveupdate', urlencode(post_fields).encode())
    request.add_header('Cookie', 'xf_user=' + urllib.parse.quote(user_id))

    # otherwise cloudflare would kick us out
    request.add_header('User-Agent', USER_AGENT)
    data = json.loads(urlopen(request).read().decode())

    print("UPDATE")

    unread = int(data[UNREAD_ALERTS_KEY])
    return unread > 0


def main():
    device = Blink1()
    config = configparser.ConfigParser()
    config.read('config.ini')

    token = config['Settings']['TOKEN']
    user_id = config['Settings']['USER_ID']
    main_loop(device, token, user_id)


def main_loop(device, token, user_id):
    unread_alert = search_updates(token, user_id)
    last_check = int(round(time.time() * 1000))
    while True:
        now = int(round(time.time() * 1000))
        if last_check + 3 * 1000 <= now:
            # update RSS FEED
            unread_alert = search_updates(token, user_id)
            last_check = now

        if unread_alert:
            device.fade_to_rgb(FADE_TIME, SPIGOT_RGB[0], SPIGOT_RGB[1], SPIGOT_RGB[2])

            time.sleep(1)

            # white
            device.fade_to_rgb(FADE_TIME, 0, 0, 0)
        else:
            time.sleep(UPDATE_INTERVAL)

# Main code
main()
