import argparse
import shutil

from .downloader import *
from .parser import webparse, parsem3u8
from .common import yuuError

def main():
    parser = argparse.ArgumentParser(prog='yuu')
    parser.add_argument('--proxies', '-p', required=False, default=None, dest='proxy', help='Use http(s)/socks5 proxies (please add `socks5://` if you use socks5)')
    parser.add_argument('--output', '-o', required=False, default=None, dest='proxy', help='Output filename')
    parser.add_argument('input', required=True, dest='url', help='AbemaTV url site')

    args = parser.parse_args()

    if args.url[-5:] != '.m3u8':
        webdata = webparse(args.url)
    if arsg.url[-5:] == '.m3u8':
        files, iv, ticket = parsem3u8(args.url)
        if args.output is None:
            yuuError('Please provide --output')


if __name__=='__main__':
    main()