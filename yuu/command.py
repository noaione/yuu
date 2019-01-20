import argparse
import shutil
import sys

from .downloader import *
from .parser import webparse, parsem3u8

def main():
    parser = argparse.ArgumentParser(prog='yuu')
    parser.add_argument('--proxies', '-p', required=False, default=None, dest='proxy', help='Use http(s)/socks5 proxies (please add `socks5://` if you use socks5)')
    parser.add_argument('--resolution', '-r', required=False, default='1080p', dest='res', choices=['180p', '240p', '360p', '480p', '720p', '1080p'], help='Resolution (Default: 1080p)')
    parser.add_argument('--output', '-o', required=False, default=None, dest='output', help='Output filename')
    parser.add_argument('input', help='AbemaTV url site or m3u8')

    args = parser.parse_args()

    if args.proxy:
        print('[INFO] Testing proxy')
        sesi = requests.Session()
        sesi.proxies = {'http': args.proxy}
        try:
            sesi.get('http://httpbin.org/get')
        except TimeoutError:
            sesi = requests.Session()
            sesi.proxies = {'https': args.proxy}
            try:
                sesi.get('http://httpbin.org/get')
            except TimeoutError:
                print('[ERROR] Cannot connect to proxy (Request timeout)')
                sys.exit(1)
    else:
        sesi = requests.Session()

    if args.input[-5:] != '.m3u8':
        print('[INFO] Parsing website')
        dltitle, eptitle, m3u8link = webparse(args.input, args.res, sesi)
        print('[INFO] Parsing m3u8')
        files, iv, ticket = parsem3u8(m3u8link, sesi)
        output = '{x} - {y} (AbemaTV {z}).ts'.format(x=dltitle, y=eptitle, z=args.res)
    if arsg.input[-5:] == '.m3u8':
        print('[INFO] Parsing m3u8')
        files, iv, ticket = parsem3u8(args.input, sesi)
        if args.output is None:
            print('[ERROR] Please provide output')
            sys.exit(1)
        output = args.output + '.ts'

    print('[INFO] Fetching user token')
    authtoken = getAuthToken(sesi)
    print('[INFO] Fetching m3u8 key')
    getkey = fetchVideoKey(ticket, authtoken, sesi)
    
    print('[INFO][DOWN] Starting downloader...')
    dllist, tempdir = getVideo(files, getkey, iv, authtoken[0], sesi)
    print('[INFO][DOWN] Finished downloading')
    print('[INFO] Merging video')
    mergeVideo(dllist, output)
    print('[INFO] Finished merging')

    print('[INFO] Cleaning up')
    shutil.rmtree(tempdir)
    sys.exit(0)

if __name__=='__main__':
    main()