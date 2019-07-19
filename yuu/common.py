import os
import json
import re

from .ext import *

__version__ = "1.0.0"

def is_channel(url):
    url = re.findall('(slot)', url)
    if url:
        return True
    return False


def get_parser(url):
    valid_abema = r'https?://(?:abema\.tv)/(?:channels|video)/(?:\w*)(?:/|-\w*/)((?P<slot>slots/)|)(?P<video_id>.*[^-_])'
    valid_gyao = r'(?isx)http(?:|s)://gyao.yahoo.co.jp/(?:player|title[\w])/(?P<p1>[\w]*.*)'  
    if re.match(valid_abema, url):
        return AbemaTV
    elif re.match(valid_gyao, url):
        return GYAO
    return None


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
