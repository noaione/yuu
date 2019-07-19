import hashlib
import hmac
import json
import re
import struct
import time
import uuid
from base64 import urlsafe_b64encode
from binascii import unhexlify
from functools import partial

import m3u8
from Crypto.Cipher import AES

from .common import (_CHANNELAPI, _HKEY, _KEYPARAMS, _LICENSE_API,
                     _MEDIATOKEN_API, _PROGRAMAPI, _STRTABLE, _USERAPI,
                     is_channel)


def get_parser(url):
    if 'abema.tv' in url:
        return AbemaTV
    elif 'gyao.yahoo.co.jp' in url:
        return GYAO
    else:
        return None


class AbemaTV:
    def __init__(self, session, verbose=False):
        self.session = session
        self.verbose = verbose
        self.type = 'AbemaTV'

        self.m3u8_url = None
        self.resolution = None
        self.ticket = None
        self.device_id = None
        self.is_m3u8 = False


    def __repr__(self):
        return '<yuu.AbemaTV: Verbose={}, Resolution={}, Device ID={}, m3u8 URL={}>'.format(self.verbose, self.resolution, self.device_id, self.m3u8_url)


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
        res = self.session.post(_USERAPI, json=json_data).json()

        try:
            if self.verbose:
                print('[DEBUG] Data sended, getting token')
            token = res['token']
            if self.verbose:
                print('[DEBUG] Usertoken: {}'.format(token))
        except:
            print('[ERROR] Failed to get usertoken')
            return None, None

        self.device_id = deviceid
        self.session.headers.update({'Authorization': 'bearer ' + token})
        #return 'bearer ' + token


    def parse(self, url, resolution=None):
        """
        Function to parse abema url
        """
        if self.verbose:
            print('[DEBUG] Requesting data to Abema API')
        if '.m3u8' in url[-5:]:
            reg = re.compile(r'(program|slot)\/[\w+-]+')
            url = re.search(reg, m3u8)[0]
            self.is_m3u8 = True
        
        ep_link = url[url.rfind('/')+1:]

        if is_channel(url):
            req = self.session.get(_CHANNELAPI + ep_link)
            if self.verbose and req.status_code == 200:
                print('[DEBUG] Data requested')
                print('[DEBUG] Parsing json API')

            jsdata = req.json()
            output_name = jsdata['slot']['title']
            if 'chasePlayback' in jsdata['slot']: # just in case
                hls = jsdata['slot']['chasePlayback']['hls']
            else:
                hls = jsdata['slot']['playback']['hls']

            m3u8_url = '{x}/{r}/playlist.m3u8'.format(x=hls[:hls.rfind('/')], r=resolution[:-1])
            if self.is_m3u8:
                m3u8_url = url

            if self.verbose:
                print('[DEBUG] M3U8 Link: {}'.format(m3u8_url))
                print('[DEBUG] Title: {}'.format(output_name))
        else:
            req = self.session.get(_PROGRAMAPI + ep_link)
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
                m3u8_url = url

            if self.verbose:
                print('[DEBUG] M3U8 Link: {}'.format(m3u8_url))
                print('[DEBUG] Video title: {}'.format(title))
                print('[DEBUG] Episode number: {}'.format(epnum))

        self.resolution = resolution
        self.m3u8_url = m3u8_url
        
        return output_name


    def parse_m3u8(self):
        if self.verbose:
            print('[DEBUG] Requesting m3u8')
        r = self.session.get(self.m3u8_url)

        if self.verbose and r.status_code == 200:
            if r.status_code == 200:
                print('[DEBUG] m3u8 requested')
                print('[DEBUG] Parsing m3u8')
            elif r.status_code == 403:
                print('[DEBUG] Forbidden access to the m3u8 url')
                print('[DEBUG] Probably a premium video.')

        if r.status_code == 403:
            print('[ERROR] Video are geo-locked to Japanese only.')
            if self.verbose:
                print('[ERROR] Code 403: ' + r.text)
            return None, None

        x = m3u8.loads(r.text)
        files = x.files[1:]
        if not files[0]:
            files = files[1:]
        resgex = re.findall(r'(\d*)(?:\/\w+.ts)', files[0])[0]
        iv = x.keys[0].iv
        ticket = x.keys[0].uri[18:]

        if self.resolution[:-1] != resgex:
            print('[WARN] Resolution {} are not available'.format(self.resolution))
            print('[WARN] Switching to {}p'.format(resgex))
        if self.verbose:
            print('[DEBUG] Total files: {}'.format(len(files)))
            print('[DEBUG] IV: {}'.format(iv))
            print('[DEBUG] Ticket key: {}'.format(ticket))

        self.ticket = ticket

        files_ = []
        for f in files:
            if '?tver' in f:
                f = f[:f.find('?tver')]
            files_.append(f)

        return files_, iv[2:]


    def get_video_key(self):
        if self.verbose:
            print('[DEBUG] Sending parameter to API')
        restoken = self.session.get(_MEDIATOKEN_API, params=_KEYPARAMS).json()
        mediatoken = restoken['token']
        if self.verbose:
            print('[DEBUG] Mediatoken: {}'.format(mediatoken))

        if self.verbose:
            print('[DEBUG] Sending ticket and mediatoken to License API')
        rgl = self.session.post(_LICENSE_API, params={"t": mediatoken}, json={"kv": "a", "lt": self.ticket})
        if rgl.status_code == 403:
            print('[ERROR] Access to the video are not allowed\nProbably a premium video or geo-locked.')
            if self.verbose:
                print('[ERROR] Code 403: ' + rgl.text)
            return None

        gl = rgl.json()

        cid = gl['cid']
        k = gl['k']

        if self.verbose:
            print('[DEBUG] CID: {}'.format(cid))
            print('[DEBUG] K: {}'.format(k))

        if self.verbose:
            print('[DEBUG] Summing up data with STRTABLE')
        res = sum([_STRTABLE.find(k[i]) * (58 ** (len(k) - 1 - i)) for i in range(len(k))])

        if self.verbose:
            print('[DEBUG] Result: {}'.format(res))
            print('[DEBUG] Intepreting data')

        encvk = struct.pack('>QQ', res >> 64, res & 0xffffffffffffffff)

        if self.verbose:
            print('[DEBUG] Encoded video key: {}'.format(encvk))
            print('[DEBUG] Hashing data')

        h = hmac.new(unhexlify(_HKEY), (cid + self.device_id).encode("utf-8"), digestmod=hashlib.sha256)
        enckey = h.digest()

        if self.verbose:
            print('[DEBUG] Second Encoded video key: {}'.format(enckey))
            print('[DEBUG] Decrypting result')

        aes = AES.new(enckey, AES.MODE_ECB)
        vkey = aes.decrypt(encvk)

        if self.verbose:
            print('[DEBUG] Decrypted, Resulting output: {}'.format(vkey))

        return vkey


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


class GYAO:
    def __init__(self, url, session, verbose=False):
        self.session = session
        self.verbose = verbose

        self.url = url
        self.m3u8_url = None
        self.resolution = None
        self.policy_key = None
        self.account = None
        self.m3u8_url_list = None
        self.is_m3u8 = False

        # Use Chrome UA
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'})


    def __repr__(self):
        return '<yuu.GYAO: Verbose={}, Resolution={}, m3u8 URL={}>'.format(self.verbose, self.resolution, self.m3u8_url)


    def get_token(self):
        headers = {'X-User-Agent': 'Unknown Pc GYAO!/2.0.0 Web'}
        query = '?fields=title%2Cid%2CvideoId'
        v_id = re.findall(r'(?isx)http(?:|s)://gyao.yahoo.co.jp/(?:player|title[\w])/(?P<p1>[\w]*.*)', self.url)
        if not v_id:
            raise ValueError('Video URL are not valid')
       
        r_vid = self.session.get('https://gyao.yahoo.co.jp/dam/v1/videos/' + v_id[0].replace('/', ':').rstrip(':') + query, headers=headers)
        r_cov = self.session.get("http://players.brightcove.net/4235717419001/default_default/index.html?videoId=" + r_vid['videoId'])
        data_account = re.findall(r'<video-js\s+[^>]*\bdata-account\s*=.([\d]*).*>', r_cov.text, re.IGNORECASE | re.DOTALL | re.VERBOSE)

        r_pk = self.session.get("http://players.brightcove.net/{}/default_default/index.html".format(data_account[0]))

        pkey = re.findall(r'policyKey\s*:\s*(["\'])(?P<pk>.+?)\1', r_pk.text)[1]

        self.account = data_account[0]
        self.policy_key = pkey


    def parse(self, resolution=None):
        """
        Function to parse gyao url
        """
        if self.verbose:
            print('[DEBUG] Requesting data to GYAO/Brightcove API')

        res_list = [
            '240p-0', '360p-0', '480p-0', '720p-0', '1080p-0',
            '240p-1', '360p-1', '480p-1', '720p-1', '1080p-1'
        ]

        if resolution not in res_list:
            raise ValueError('yuu.GYAO: Unknown resolution')

        v_id = re.findall(r'(?isx)http(?:|s)://gyao.yahoo.co.jp/(?:player|title[\w])/(?P<p1>[\w]*.*)', self.url)
        if not v_id:
            raise ValueError('yuu.GYAO: Video URL are not valid')

        headers = {'X-User-Agent': 'Unknown Pc GYAO!/2.0.0 Web'}
        r_vid = self.session.get('https://gyao.yahoo.co.jp/dam/v1/videos/' + v_id[0].replace('/', ':').rstrip(':') + '?fields=title%2Cid%2CvideoId%2CshortTitle', headers=headers).json()
        title = r_vid['title']
        ep_title = r_vid['shortTitle']

        output_name = title.replace(ep_title, '').replace('\u3000', ' ') + ' - ' + ep_title

        headers_pk = {
            'Accept': 'application/json;pk=' + self.policy_key,
        }

        req_bc = self.session.get('https://edge.api.brightcove.com/playback/v1/accounts/{}/videos/{}'.format(self.account, r_vid['videoId']), headers=headers_pk)
        if self.verbose and req_bc.status_code == 200:
            print('[DEBUG] Data requested')
            print('[DEBUG] Parsing json API')

        jsdata = req_bc.json()
        hls_list = jsdata['sources'][2]['src'] # Use EXT-V4 http version

        if self.verbose:
            print('[DEBUG] M3U8 Link: {}'.format(hls_list))
            print('[DEBUG] Title: {}'.format(output_name))

        self.m3u8_url_list = hls_list

        if self.verbose:
            print('[DEBUG] Requesting m3u8 list')
        r = self.session.get(hls_list)

        if self.verbose and r.status_code == 200:
            if r.status_code == 200:
                print('[DEBUG] m3u8 requested')
                print('[DEBUG] Parsing m3u8')
            elif r.status_code == 403:
                print('[DEBUG] Forbidden access to the m3u8 url')
                print('[DEBUG] Probably a premium video.')

        if r.status_code == 403:
            print('[ERROR] Video are geo-locked to Japanese only.')
            if self.verbose:
                print('[ERROR] Code 403: ' + r.text)
            return None, None, None

        r_all = m3u8.loads(r.text)

        res_list = []
        for r_p in r_all.playlists:
            temp_ = []
            if int(resolution[:-3]) == r_p:
                temp_.append(r_p.uri)
                temp_.append(r_p.stream_info.bandwidth)
                res_list.append(temp_)

        if len(res_list) > 1:
            if '-1' in resolution:
                calc = min
            elif '-0' in resolution:
                calc = max
            temp_n = [x[1] for x in res_list]
            res_list = res_list[temp_n.index(calc(temp_n))]
        
        self.m3u8_url = res_list[0]
        self.resolution = resolution

        return output_name


    def parse_m3u8(self):
        if self.verbose:
            print('[DEBUG] Requesting m3u8')
        r = self.session.get(self.m3u8_url)

        if self.verbose and r.status_code == 200:
            if r.status_code == 200:
                print('[DEBUG] m3u8 requested')
                print('[DEBUG] Parsing m3u8')
            elif r.status_code == 403:
                print('[DEBUG] Forbidden access to the m3u8 url')
                print('[DEBUG] Probably a premium video.')

        if r.status_code == 403:
            print('[ERROR] Video are geo-locked to Japanese only.')
            if self.verbose:
                print('[ERROR] Code 403: ' + r.text)
            return None, None

        x = m3u8.loads(r.text)
        files = x.files

        if self.verbose:
            print('[DEBUG] Total files: {}'.format(len(files)))

        return files, None


    def resolutions(self):
        if self.verbose:
            print('[DEBUG] Requesting data to API')

        r_all = m3u8.loads(self.session.get(self.m3u8_url_list).text)

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