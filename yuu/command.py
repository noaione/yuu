import argparse
import shutil
import sys

from .downloader import *
from .parser import webparse, parsem3u8
from .common import __version__

def main():
    parser = argparse.ArgumentParser(prog='yuu', description='A simple AbemaTV video ripper', epilog='Created by NoAiOne - Version {v}'.format(v=__version__))
    parser.add_argument('--proxies', '-p', required=False, default=None, dest='proxy', help='Use http(s)/socks5 proxies (please add `socks5://` if you use socks5)')
    parser.add_argument('--resolution', '-r', required=False, default='1080p', dest='res', choices=['180p', '240p', '360p', '480p', '720p', '1080p'], help='Resolution (Default: 1080p)')
    parser.add_argument('--output', '-o', required=False, default=None, dest='output', help='Output filename')
    parser.add_argument('--version', '-v', action='version', version='%(prog)s {v} - Created by NoAiOne'.format(v=__version__))
    parser.add_argument('input', help='AbemaTV url site or m3u8')

    args = parser.parse_args()
    print('[INFO] Starting yuu...')

    if args.proxy:
        print('[INFO] Testing proxy')
        sesi = requests.Session()
        sesi.proxies = {'http': args.proxy}
        # Someebody tell me to do recursive test properly
        try:
            sesi.get('http://httpbin.org/get') # Some test website to check if proxy works or not
        except TimeoutError:
            sesi = requests.Session()
            sesi.proxies = {'https': args.proxy}
            try:
                sesi.get('http://httpbin.org/get') # This too but in https mode
            except TimeoutError:
                sesi = requests.Session()
                sesi.proxies = {'http': args.proxy, 'https': args.proxy} # Final test if it's failed then it will return error
                try:
                    sesi.get('http://httpbin.org/get')
                except:
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
    elif args.input[-5:] == '.m3u8':
        print('[INFO] Parsing m3u8')
        files, iv, ticket = parsem3u8(args.input, sesi)
        if args.output is None:
            print('[ERROR] Please provide output')
            sys.exit(1)
        output = args.output + '.ts'

    print('[INFO] Fetching user token')
    authtoken = getAuthToken(sesi)
    sesi.headers.update({'Authorization': authtoken[0]})
    print('[INFO] Fetching m3u8 key')
    getkey = fetchVideoKey(ticket, authtoken, sesi)
    
    print('[INFO][DOWN] Starting downloader...')
    dllist, tempdir = getVideo(files, getkey, iv, sesi)
    print('[INFO][DOWN] Finished downloading')
    print('[INFO] Merging video')
    mergeVideo(dllist, output)
    print('[INFO] Finished merging')

    print('[INFO] Cleaning up')
    shutil.rmtree(tempdir)
    sys.exit(0)

if __name__=='__main__':
    main()