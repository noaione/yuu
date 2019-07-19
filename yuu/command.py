import os
import shutil
import subprocess

import click
import requests

from .common import __version__, isUserAdmin, res_data
from .downloader import download_chunk, merge_video
from .parser import get_parser

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], ignore_unknown_options=True)

@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.option('--version', '-V', is_flag=True, help="Show current version")
@click.option('--update', '-U', is_flag=True, help="Update yuu to the newest version")
def cli(version=False, update=False):
    """
    A simple AbemaTV video downloader
    """
    if version:
        print('yuu v{} - Created by NoAiOne'.format(__version__))
        exit(0)
    if update:
        print('[INFO] Updating yuu...'.format(ver=__version__))
        upstream_data = requests.get("https://pastebin.com/raw/Bt3ZLjfu").json()
        upstream_version = upstream_data['version']
        upstream_change = upstream_data['changelog']
        if upstream_version == __version__:
            print('[INFO] Already on the newest version.')
            exit(0)
        print('[INFO] Updating to yuu version {} (Current: v{})'.format(upstream_version, __version__))

        try:
            if isUserAdmin():
                if os.name != "nt":
                    print('[WARN] Run this command to update yuu: `pip3 install -U yuu=={}`'.format(upstream_version))
                    exit(1)
                from win32com.shell.shell import ShellExecuteEx
                ShellExecuteEx(lpVerb='runas', lpFile='pip', lpParameters='install -U yuu=={}'.format(upstream_version))
            else:
                print('[WARN] Run this command to update yuu: `pip install -U yuu=={}`'.format(upstream_version))
                exit(1)
        except:
            print('[ERROR] Updater returned non-zero exit code')
            print('Try to run `pip install -U yuu={}` manually'.format(upstream_version))
            exit(1)
        print('\n=== yuu version {} changelog ==='.format(upstream_version))
        print(upstream_change+'\n')
        print('[INFO] Updated.')
        exit(0)


# @cli.command("download", short_help="Download video from abema.tv")
# @click.argument("input", metavar="<AbemaTV url site or m3u8>")
# @click.option("--proxy", "-p", required=False, default=None, metavar="<ip:port/url>", help="Use http(s)/socks5 proxies (please add `socks5://` if you use socks5)")
# @click.option("--resolution", "-r", "res", required=False, type=click.Choice(['180p', '240p', '360p', '480p', '720p', '1080p']), default="1080p", help="Resolution to be downloaded (Default: 1080p)")
# @click.option("--resolutions", "-R", "resR", is_flag=True, help="Show available resolutions")
# @click.option("--output", "-o", required=False, default=None, help="Output filename")
# @click.option('--verbose', '-v', is_flag=True, help="Enable verbosity")
# def main_downloaderv2(input, proxy, res, resR, output, verbose):
#     print('[INFO] Starting yuu v{ver}...'.format(ver=__version__))

#     upstream_data = requests.get("https://pastebin.com/raw/Bt3ZLjfu").json()
#     upstream_version = upstream_data['version']
#     if upstream_version != __version__:
#         print('[INFO] There\'s new version available to download, please update using `yuu -U`.')
#         exit(0)


@cli.command("download", short_help="Download video from abema.tv")
@click.argument("input", metavar="<AbemaTV url site or m3u8>")
@click.option("--proxy", "-p", required=False, default=None, metavar="<ip:port/url>", help="Use http(s)/socks5 proxies (please add `socks5://` if you use socks5)")
@click.option("--resolution", "-r", "res", required=False, type=click.Choice(['180p', '240p', '360p', '480p', '720p', '1080p']), default="1080p", help="Resolution to be downloaded (Default: 1080p)")
@click.option("--resolutions", "-R", "resR", is_flag=True, help="Show available resolutions")
@click.option("--output", "-o", required=False, default=None, help="Output filename")
@click.option('--verbose', '-v', is_flag=True, help="Enable verbosity")
def main_downloader(input, proxy, res, resR, output, verbose):
    """Download a free video from abema"""
    print('[INFO] Starting yuu v{ver}...'.format(ver=__version__))

    #upstream_data = requests.get("https://pastebin.com/raw/Bt3ZLjfu").json()
    #upstream_version = upstream_data['version']
    #if upstream_version != __version__:
    #    print('[INFO] There\'s new version available to download, please update using `yuu -U`.')
    #    exit(0)

    sesi = requests.Session()
    if proxy:
        print('[INFO] Testing proxy')
        proxy_test = [
            {'http': proxy, 'https': proxy},
            {'https': proxy},
            {'http': proxy}
        ]
        for mode in proxy_test:
            try:
                if verbose:
                    print('Testing {x} mode proxy'.format(x="+".join(mode.keys())))
                sesi.proxies = mode
                sesi.get('http://httpbin.org/get') # Test website to check if proxy works or not
                pmode = "+".join(mode.keys()).upper() + "/SOCKS5"
            except requests.exceptions.RequestException:
                if verbose:
                    print('[DEBUG] Failed')
                if mode == proxy_test[-1]:
                    print('[ERROR] Cannot connect to proxy (Request timeout)')
                    exit(1)
        sesi.proxies = {'http': proxy, 'https': proxy}
    try:
        sesi.get('http://httpbin.org/get')
        pmode = "No proxy"
    except:
        print('[ERROR] No connection available to make requests')
        exit(1)
    if verbose:
        print('[DEBUG] Using proxy mode: {}'.format(pmode))

    yuuParser = get_parser(input)

    if not yuuParser:
        print('[ERROR] Unknown url')
        exit(1)

    yuuParser = yuuParser(sesi, verbose)

    if 'AbemaTV' in yuuParser.type:
        mode = 'AbemaTV'
    elif 'GYAO' in yuuParser.type:
        mode = 'GYAO'

    print('[INFO] {}: Fetching user token'.format(mode))
    yuuParser.get_token()

    print('[INFO] {}: Parsing url'.format(mode))
    output_name = yuuParser.parse(input, res)
    if resR:
        print('[INFO] {}: Checking available resolution'.format(mode))
        avares = yuuParser.resolutions()
        print('[INFO] {}: Available resolution:'.format(mode))
        print('{0: <{width}}{1: <{width}}{2: <{width}}{3: <{width}}'.format("", "Resolution", "Video Quality", "Audio Quality", width=16))
        for res in avares:
            r_c, wxh = res
            vidq, audq = res_data[r_c]
            print('{0: <{width}}{1: <{width}}{2: <{width}}{3: <{width}}'.format('>> ' + r_c, wxh, vidq, audq, width=16))
        exit(0)

    if output:
        if output[-3:] == '.ts':
            output = output
        else:
            output = output + '.ts'
    else:
        output = '{x} (AbemaTV {r}).ts'.format(x=output_name, r=res)

    print('[INFO] {}: Parsing m3u8'.format(mode))
    files, iv = yuuParser.parse_m3u8()

    illegalchar = ['/', '<', '>', ':', '"', '\\', '|', '?', '*'] # https://docs.microsoft.com/en-us/windows/desktop/FileIO/naming-a-file
    for char in illegalchar:
        output = output.replace(char, '_')

    print('[INFO] {}: Fetching video key'.format(mode))
    video_key = yuuParser.get_video_key()#fetch_video_key(ticket, authtoken, sesi, verbose)

    print('[INFO][DOWN] Starting downloader...')
    print('[INFO][DOWN] Output: {}'.format(output))
    print('[INFO][DOWN] Resolution: {}'.format(res))
    dl_list, temp_dir = download_chunk(files, video_key, iv, yuuParser.session)
    if not dl_list:
        if temp_dir:
            shutil.rmtree(temp_dir)
        exit(1)
    print('[INFO][DOWN] Finished downloading')
    print('[INFO][DOWN] Merging video')
    merge_video(dl_list, temp_dir)
    shutil.rmtree(temp_dir)
    print('[INFO] Finished downloading: {}'.format(output))
    exit(0)


def main():
    cli()


if __name__=='__main__':
    cli()
