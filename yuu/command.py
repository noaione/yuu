import argparse
import shutil

from .downloader import *
from .parser import webparse, parsem3u8
from .common import yuuError

def main():
    parser = argparse.ArgumentParser(prog='yuu')
    parser.add_argument('--proxies', '-p', required=False, default=None, dest='proxy', help='Use http(s)/socks5 proxies (please add `socks5://` if you use socks5)')
    parser.add_argument('--resolution', '-r', required=False, default='1080p', dest='res', choices=['180p', '240p', '360p', '480p', '720p', '1080p'], help='Resolution (Default: 1080p)')
    parser.add_argument('--output', '-o', required=False, default=None, dest='output', help='Output filename')
    parser.add_argument('input', help='AbemaTV url site or m3u8')

    args = parser.parse_args()

    if args.input[-5:] != '.m3u8':
        print('@@ Parsing website')
        dltitle, eptitle, m3u8link = webparse(args.input, args.res)
        print('@@ Parsing m3u8')
        files, iv, ticket = parsem3u8(m3u8link, args.proxy)
        output = '{x} - {y} (AbemaTV {z}).ts'.format(x=dltitle, y=eptitle, z=args.res)
    if arsg.input[-5:] == '.m3u8':
        print('@@ Parsing m3u8')
        files, iv, ticket = parsem3u8(args.input, args.proxy)
        if args.output is None:
            yuuError('Please provide --output')
        output = args.output + '.ts'

    print('@@ Fetching user token')
    authtoken = getAuthToken(args.proxy)
    print('@@ Fetching m3u8 key')
    getkey = fetchVideoKey(ticket, authtoken, args.proxy)
    
    print('@@ Starting downloader...')
    dllist, tempdir = getVideo(files, getkey, iv, authtoken[0], args.proxy)
    print('@@ Finished downloading')
    print('@@ Merging video')
    mergeVideo(dllist, output)
    print('@@ Finished merging')

    print('@@ Cleaning up')
    shutil.rmtree(tempdir)

if __name__=='__main__':
    main()