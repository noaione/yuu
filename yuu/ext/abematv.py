import hashlib
import hmac
import json
import os
import re
import struct
import tempfile
import time
import uuid
from base64 import urlsafe_b64encode
from binascii import unhexlify

import m3u8
from Crypto.Cipher import AES
from tqdm import tqdm


def is_channel(url):
    url = re.findall('(slot)', url)
    if url:
        return True
    return False


class AbemaTVDownloader:
    def __init__(self, files, key, iv, session):
        self.files = files
        self.key = key
        self.iv = iv
        self.session = session

        self.downloaded_files = []
        self.merge = True

        if os.name == "nt":
            yuu_folder = os.path.join(os.getenv('LOCALAPPDATA'), 'yuu_data')
        else:
            yuu_folder = os.path.join(os.getenv('HOME'), '.yuu_data')
        if not os.path.isdir(yuu_folder):
            os.mkdir(yuu_folder)

        self.temporary_folder = tempfile.mkdtemp(dir=yuu_folder)

        self._aes = None


    def setup_decryptor(self):
        if self.iv.startswith('0x'):
            self.iv = self.iv[2:]
        self.iv = unhexlify(self.iv)
        self._aes = AES.new(self.key, AES.MODE_CBC, IV=self.iv)


    def download_chunk(self):
        self.setup_decryptor() # Initialize a new decryptor
        try:
            with tqdm(total=len(self.files), desc='Downloading', ascii=True, unit='file') as pbar:
                for tsf in self.files:
                    outputtemp = self.temporary_folder + '\\' + os.path.basename(tsf)
                    if outputtemp.find('?tver') != -1:
                        outputtemp = outputtemp[:outputtemp.find('?tver')]
                    with open(outputtemp, 'wb') as outf:
                        try:
                            vid = self.session.get(tsf)
                            vid = self._aes.decrypt(vid.content)
                            outf.write(vid)
                        except Exception as err:
                            print('[ERROR] Problem occured\nreason: {}'.format(err))
                            return None, self.temporary_folder
                    pbar.update()
                    self.downloaded_files.append(outputtemp)
        except KeyboardInterrupt:
            print('[WARN] User pressed CTRL+C, cleaning up...')
            return None, self.temporary_folder
        return self.downloaded_files, self.temporary_folder


class AbemaTV:
    def __init__(self, url, session, verbose=False):
        self.session = session
        self.verbose = verbose
        self.type = 'AbemaTV'

        self.url = url
        self.m3u8_url = None
        self.resolution = None
        self.ticket = None
        self.device_id = None
        self.is_m3u8 = False
        self.est_filesize = None # In MiB

        self.resolution_data = {
            "1080p": ["4000kb/s", "AAC 192kb/s 2ch"],
            "720p": ["2000kb/s", "AAC 160kb/s 2ch"],
            "480p": ["900kb/s", "AAC 128kb/s 2ch"],
            "360p": ["550kb/s", "AAC 128kb/s 2ch"],
            "240p": ["240kb/s", "AAC 64kb/s 1ch"],
            "180p": ["120kb/s", "AAC 64kb/s 1ch"]
        }

        self.bitrate_calculation = {
            "1080p": 5175,
            "720p": 2373,
            "480p": 1367,
            "360p": 878,
            "240p": 292,
            "180p": 179
        }

        self.authorization_required = False
        self.authorized = True # Ignore for now
        self.authorize = True # Ignore for now

        self._STRTABLE = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        self._HKEY = b"3AF0298C219469522A313570E8583005A642E73EDD58E3EA2FB7339D3DF1597E"

        self._KEYPARAMS = {
            "osName": "android",
            "osVersion": "6.0.1",
            "osLand": "ja_JP",
            "osTimezone": "Asia/Tokyo",
            "appId": "tv.abema",
            "appVersion": "3.27.1"
        }

        self._MEDIATOKEN_API = "https://api.abema.io/v1/media/token"
        self._LICENSE_API = "https://license.abema.io/abematv-hls"
        self._USERAPI = "https://api.abema.io/v1/users"
        self._PROGRAMAPI = 'https://api.abema.io/v1/video/programs/'
        self._CHANNELAPI = 'https://api.abema.io/v1/media/slots/'


    def __repr__(self):
        return '<yuu.AbemaTV: Verbose={}, Resolution={}, Device ID={}, m3u8 URL={}>'.format(self.verbose, self.resolution, self.device_id, self.m3u8_url)

    def get_downloader(self, files, key, iv):
        """
        Return a :class: of the Downloader
        """
        return AbemaTVDownloader(files, key, iv, self.session)

    def get_token(self):
        def key_secret(devid):
            SECRETKEY = (b"v+Gjs=25Aw5erR!J8ZuvRrCx*rGswhB&qdHd_SYerEWdU&a?3DzN9B"
                        b"Rbp5KwY4hEmcj5#fykMjJ=AuWz5GSMY-d@H7DMEh3M@9n2G552Us$$"
                        b"k9cD=3TxwWe86!x#Zyhe")
            deviceid = devid.encode("utf-8")
            ts_1hour = (int(time.time()) + 60 * 60) // 3600 * 3600
            time_struct = time.gmtime(ts_1hour)
            ts_1hour_str = str(ts_1hour).encode("utf-8")

            h = hmac.new(SECRETKEY, digestmod=hashlib.sha256)
            h.update(SECRETKEY)
            tmp = h.digest()

            for _ in range(time_struct.tm_mon):
                h = hmac.new(SECRETKEY, digestmod=hashlib.sha256)
                h.update(tmp)
                tmp = h.digest()

            h = hmac.new(SECRETKEY, digestmod=hashlib.sha256)
            h.update(urlsafe_b64encode(tmp).rstrip(b"=") + deviceid)
            tmp = h.digest()

            for _ in range(time_struct.tm_mday % 5):
                h = hmac.new(SECRETKEY, digestmod=hashlib.sha256)
                h.update(tmp)
                tmp = h.digest()

            h = hmac.new(SECRETKEY, digestmod=hashlib.sha256)
            h.update(urlsafe_b64encode(tmp).rstrip(b"=") + ts_1hour_str)
            tmp = h.digest()

            for _ in range(time_struct.tm_hour % 5):  # utc hour
                h = hmac.new(SECRETKEY, digestmod=hashlib.sha256)
                h.update(tmp)
                tmp = h.digest()

            finalize = urlsafe_b64encode(tmp).rstrip(b"=").decode("utf-8")

            if self.verbose:
                print('[DEBUG] Secret Key: {}'.format(finalize))

            return finalize

        deviceid = str(uuid.uuid4())
        if self.verbose:
            print('[DEBUG] Generated Device UUID: {}'.format(deviceid))
        json_data = {"deviceId": deviceid, "applicationKeySecret": key_secret(deviceid)}

        if self.verbose:
            print('[DEBUG] Sending json data')
        res = self.session.post(self._USERAPI, json=json_data).json()

        try:
            if self.verbose:
                print('[DEBUG] Data sended, getting token')
            token = res['token']
            if self.verbose:
                print('[DEBUG] Usertoken: {}'.format(token))
        except:
            return None, 'Failed to get usertoken.'

        self.device_id = deviceid
        self.session.headers.update({'Authorization': 'bearer ' + token})

        return 'Success', 'Success'


    def parse(self, resolution=None, check_only=False):
        """
        Function to parse abema url
        """

        res_list = [
            '180p', '240p', '360p', '480p', '720p', '1080p', 'best', 'worst'
        ]

        if resolution not in res_list:
            if not check_only:
                return None, 'Resolution {} are non-existant. (Check it with `-R`)'.format(resolution)

        if resolution == 'best':
            resolution = '1080p'
        if resolution == 'worst':
            resolution = '180p'

        if self.verbose:
            print('[DEBUG] Requesting data to Abema API')
        if '.m3u8' in self.url[-5:]:
            reg = re.compile(r'(program|slot)\/[\w+-]+')
            self.url = re.search(reg, m3u8)[0]
            self.is_m3u8 = True

        ep_link = self.url[self.url.rfind('/')+1:]

        if is_channel(self.url):
            req = self.session.get(self._CHANNELAPI + ep_link)
            if self.verbose and req.status_code == 200:
                print('[DEBUG] Data requested')
                print('[DEBUG] Parsing json API')

            jsdata = req.json()
            output_name = jsdata['slot']['title']
            if 'playback' in jsdata['slot']:
                hls = jsdata['slot']['playback']['hls']
            else:
                hls = jsdata['slot']['chasePlayback']['hls']  # Compat

            m3u8_url = '{x}/{r}/playlist.m3u8'.format(x=hls[:hls.rfind('/')], r=resolution[:-1])
            if self.is_m3u8:
                m3u8_url = self.url

            if self.verbose:
                print('[DEBUG] M3U8 Link: {}'.format(m3u8_url))
                print('[DEBUG] Title: {}'.format(output_name))
        else:
            req = self.session.get(self._PROGRAMAPI + ep_link)
            if self.verbose and req.status_code == 200:
                print('[DEBUG] Data requested')
                print('[DEBUG] Parsing json API')
            jsdata = req.json()
            title = jsdata['series']['title']
            epnum = jsdata['episode']['title']
            hls = jsdata['playback']['hls']
            output_name = title + ' - ' + epnum

            m3u8_url = '{x}/{r}/playlist.m3u8'.format(x=hls[:hls.rfind('/')], r=resolution[:-1])
            if self.is_m3u8:
                m3u8_url = self.url

            if self.verbose:
                print('[DEBUG] M3U8 Link: {}'.format(m3u8_url))
                print('[DEBUG] Video title: {}'.format(title))
                print('[DEBUG] Episode number: {}'.format(epnum))

        self.resolution = resolution
        self.m3u8_url = m3u8_url

        return output_name, 'Success'


    def parse_m3u8(self):
        if self.verbose:
            print('[DEBUG] Requesting m3u8')
        r = self.session.get(self.m3u8_url)

        if self.verbose and r.status_code == 200:
            if r.status_code == 200:
                print('[DEBUG] m3u8 requested')
                print('[DEBUG] Parsing m3u8')

        if r.status_code == 403:
            return None, None, 'Video are geo-locked to Japanese only.'

        x = m3u8.loads(r.text)
        files = x.files[1:]
        if not files[0]:
            files = files[1:]
        resgex = re.findall(r'(\d*)(?:\/\w+.ts)', files[0])[0]
        iv = x.keys[0].iv
        ticket = x.keys[0].uri[18:]

        if self.resolution[:-1] != resgex:
            self.resolution = resgex + 'p'
        if self.verbose:
            print('[DEBUG] Total files: {}'.format(len(files)))
            print('[DEBUG] IV: {}'.format(iv))
            print('[DEBUG] Ticket key: {}'.format(ticket))

        n = 0.0
        for seg in x.segments:
            n += seg.duration

        self.est_filesize = round((round(n) * self.bitrate_calculation[self.resolution]) / 1024 / 6, 2)
        self.ticket = ticket

        return files, iv[2:], 'Success'


    def get_video_key(self):
        if self.verbose:
            print('[DEBUG] Sending parameter to API')
        restoken = self.session.get(self._MEDIATOKEN_API, params=self._KEYPARAMS).json()
        mediatoken = restoken['token']
        if self.verbose:
            print('[DEBUG] Mediatoken: {}'.format(mediatoken))

        if self.verbose:
            print('[DEBUG] Sending ticket and mediatoken to License API')
        rgl = self.session.post(self._LICENSE_API, params={"t": mediatoken}, json={"kv": "a", "lt": self.ticket})
        if rgl.status_code == 403:
            return None, 'Access to the video are not allowed\nProbably a premium video or geo-locked.'

        gl = rgl.json()

        cid = gl['cid']
        k = gl['k']

        if self.verbose:
            print('[DEBUG] CID: {}'.format(cid))
            print('[DEBUG] K: {}'.format(k))

        if self.verbose:
            print('[DEBUG] Summing up data with STRTABLE')
        res = sum([self._STRTABLE.find(k[i]) * (58 ** (len(k) - 1 - i)) for i in range(len(k))])

        if self.verbose:
            print('[DEBUG] Result: {}'.format(res))
            print('[DEBUG] Intepreting data')

        encvk = struct.pack('>QQ', res >> 64, res & 0xffffffffffffffff)

        if self.verbose:
            print('[DEBUG] Encoded video key: {}'.format(encvk))
            print('[DEBUG] Hashing data')

        h = hmac.new(unhexlify(self._HKEY), (cid + self.device_id).encode("utf-8"), digestmod=hashlib.sha256)
        enckey = h.digest()

        if self.verbose:
            print('[DEBUG] Second Encoded video key: {}'.format(enckey))
            print('[DEBUG] Decrypting result')

        aes = AES.new(enckey, AES.MODE_ECB)
        vkey = aes.decrypt(encvk)

        if self.verbose:
            print('[DEBUG] Decrypted, Resulting output: {}'.format(vkey))

        return vkey, 'Success getting video key'


    def resolutions(self):
        if self.verbose:
            print('[DEBUG] Requesting data to API')

        m3u8_ = self.m3u8_url[:self.m3u8_url.rfind('/')]
        m3u8_1080 = m3u8_[:m3u8_.rfind('/')] + '/1080/playlist.m3u8'
        m3u8_720 = m3u8_[:m3u8_.rfind('/')] + '/720/playlist.m3u8'
        m3u8_480 = m3u8_[:m3u8_.rfind('/')] + '/480/playlist.m3u8'
        m3u8_360 = m3u8_[:m3u8_.rfind('/')] + '/360/playlist.m3u8'
        m3u8_240 = m3u8_[:m3u8_.rfind('/')] + '/240/playlist.m3u8'
        m3u8_180 = m3u8_[:m3u8_.rfind('/')] + '/180/playlist.m3u8'

        r_all = m3u8.loads(self.session.get(m3u8_[:m3u8_.rfind('/')] + '/playlist.m3u8').text)
        r1080 = m3u8.loads(self.session.get(m3u8_1080).text)
        r720 = m3u8.loads(self.session.get(m3u8_720).text)
        r480 = m3u8.loads(self.session.get(m3u8_480).text)
        r360 = m3u8.loads(self.session.get(m3u8_360).text)
        r240 = m3u8.loads(self.session.get(m3u8_240).text)
        r180 = m3u8.loads(self.session.get(m3u8_180).text)

        play_res = []
        for r_p in r_all.playlists:
            play_res.append(list(r_p.stream_info.resolution))

        x1080 = r1080.files[1:][5]
        x720 = r720.files[1:][5]
        x480 = r480.files[1:][5]
        x360 = r360.files[1:][5]
        x240 = r240.files[1:][5]
        x180 = r180.files[1:][5]

        resgex = re.compile(r'(\d*)(?:\/\w+.ts)')

        ava_reso = []
        if '1080' in re.findall(resgex, x1080):
            temp_ = ['1080p']
            for r in play_res:
                if 1080 in r:
                    temp_.append('{w}x{h}'.format(w=r[0], h=r[1]))
            ava_reso.append(temp_)
        if '720' in re.findall(resgex, x720):
            temp_ = ['720p']
            for r in play_res:
                if 720 in r:
                    temp_.append('{w}x{h}'.format(w=r[0], h=r[1]))
            ava_reso.append(temp_)
        if '480' in re.findall(resgex, x480):
            temp_ = ['480p']
            for r in play_res:
                if 480 in r:
                    temp_.append('{w}x{h}'.format(w=r[0], h=r[1]))
            ava_reso.append(temp_)
        if '360' in re.findall(resgex, x360):
            temp_ = ['360p']
            for r in play_res:
                if 360 in r:
                    temp_.append('{w}x{h}'.format(w=r[0], h=r[1]))
            ava_reso.append(temp_)
        if '240' in re.findall(resgex, x240):
            temp_ = ['240p']
            for r in play_res:
                if 240 in r:
                    temp_.append('{w}x{h}'.format(w=r[0], h=r[1]))
            ava_reso.append(temp_)
        if '180' in re.findall(resgex, x180):
            temp_ = ['180p']
            for r in play_res:
                if 180 in r:
                    temp_.append('{w}x{h}'.format(w=r[0], h=r[1]))
            ava_reso.append(temp_)

        return ava_reso

    def check_output(self, output=None, output_name=None):
        if output:
            fn_, ext_ = os.path.splitext(output)
            if ext_ != 'ts':
                output = fn_ + '.ts'
        else:
            output = '{x} ({m} {r}).ts'.format(x=output_name, m=self.type, r=self.resolution)

        return output
