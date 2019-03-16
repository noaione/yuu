import re

__version__ = '0.1.4.2'

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
	url = re.findall('(slots)', url)
	if not url:
		return True
	return False
