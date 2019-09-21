# Will be added depending on the situation
# Still need to figure out some encryption in the Authorization Header

# Authorization Header are different while parsing the web and fetching key + m3u8 + video.

# Authorization header used while fetching key and m3u8 are encrypted with AES-CTR-128
# They add a current time in milisecond to the original Authorization and encrypt it with them
# Example: eyRasdiuahsidhqwe|1563504400803
# Then they'll encrypt that
# After that, the encrypted are decoded as Hex and appended `1563504400803` time again
# Example: rrqiweuosjaod|1563504400803
# That will be used as the new Authorization.
# They use a counter that I still need to understand because the javascript are obfuscated

# Need help to deobfuscate the javascript that used to encrypt the Header
# If anyone interested at helping me, contact me at Discord: N4O#8868
# Or email me at: noaione0809@gmail.com

import hashlib
import hmac
import json
import re
import struct
import time
import uuid
from base64 import urlsafe_b64encode
from binascii import unhexlify

import m3u8
from Crypto.Cipher import AES

class Ponimu:
    def __init__(self, session, verbose=False):
        self.session = session
        self.verbose = verbose
        self.type = 'AbemaTV'

        self.m3u8_url = None
        self.resolution = None
        self.is_m3u8 = False

        self.resolution_data = {
            "1080p": ["4000kb/s", "AAC 192kb/s 2ch"],
            "720p": ["2000kb/s", "AAC 160kb/s 2ch"],
            "480p": ["900kb/s", "AAC 128kb/s 2ch"],
            "360p": ["550kb/s", "AAC 128kb/s 2ch"],
        }

        self.ENCRYPTIONKEY = "Halo2139!234well"
        self.authorization_token = None
        self.authorization_required = True
        self.authorized = False

        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'})

    def __repr__(self):
        return '<yuu.Ponimu: Verbose={}, Resolution={}, m3u8 URL={}>'.format(self.verbose, self.resolution, self.m3u8_url)

    def authorization_obsfucating(self):
        # Need to deobfuscate javascript
        return None

    

    def authorize(self, username, password):
        _AUTH_URL = 'https://api.ponimu.com/api/authenticate'
        creds = {
            'username': username,
            'password': password
        }
        
        r = self.session.post(_AUTH_URL, json=creds)
        js_r = r.json()
        if r.status_code != 200:
            return False, js_r['title'] + ': ' + js_r['detail']
        
        self.authorization_token = r['id_token']
        self.authorized = True
        return True
        