import os
import json
import re

__version__ = "1.0.0"

_STRTABLE = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_HKEY = b"3AF0298C219469522A313570E8583005A642E73EDD58E3EA2FB7339D3DF1597E"

_KEYPARAMS = {
    "osName": "android",
    "osVersion": "6.0.1",
    "osLand": "ja_JP",
    "osTimezone": "Asia/Tokyo",
    "appId": "tv.abema",
    "appVersion": "3.27.1"
}

_MEDIATOKEN_API = "https://api.abema.io/v1/media/token"
_LICENSE_API = "https://license.abema.io/abematv-hls"
_USERAPI = "https://api.abema.io/v1/users"
_PROGRAMAPI = 'https://api.abema.io/v1/video/programs/'
_CHANNELAPI = 'https://api.abema.io/v1/media/slots/'

def is_channel(url):
    url = re.findall('(slot)', url)
    if url:
        return True
    return False


abema_data = {
    "1080p": ["4000kb/s", "AAC 192kb/s 2ch"],
    "720p": ["2000kb/s", "AAC 160kb/s 2ch"],
    "480p": ["900kb/s", "AAC 128kb/s 2ch"],
    "360p": ["550kb/s", "AAC 128kb/s 2ch"],
    "240p": ["240kb/s", "AAC 64kb/s 1ch"],
    "180p": ["120kb/s", "AAC 64kb/s 1ch"]
}

abema_data = {
    "1080p-0": ["~5000kb/s", "AAC 64kb/s 2ch"],
    "720p-0": ["2000kb/s", "AAC 64kb/s 2ch"],
    "480p-0": ["900kb/s", "AAC 64kb/s 2ch"],
    "360p-0": ["550kb/s", "AAC 64kb/s 2ch"],
    "240p-0": ["~200kb/s", "AAC 64kb/s 1ch"],
    "1080p-1": ["~5000kb/s", "AAC 128kb/s 2ch"],
    "720p-1": ["~2000kb/s", "AAC 128kb/s 2ch"],
    "480p-1": ["~900kb/s", "AAC 128kb/s 2ch"],
    "360p-1": ["~550kb/s", "AAC 128kb/s 2ch"],
    "240p-1": ["~200kb/s", "AAC 128kb/s 2ch"],
}

"""
Admin Check Code from https://gist.github.com/sylvainpelissier/ff072a6759082590a4fe8f7e070a4952
"""
def isUserAdmin():
    if os.name == 'nt':
        import ctypes
        # WARNING: requires Windows XP SP2 or higher!
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            print("Admin check failed, assuming not an admin.")
            return False
    else:
        return os.getuid() == 0


def read_yuu_data(path):
    if not os.path.isfile(os.path.join(path, 'yuu_download.json')):
        with open(os.path.join(path, 'yuu_download.json'), 'w') as f:
            f.write(r'{}')
    with open(os.path.join(path, 'yuu_download.json')) as f:
        return json.load(f)
