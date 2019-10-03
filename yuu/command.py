import os
import shutil
import subprocess

import click
import requests

from .common import __version__, isUserAdmin, get_parser, merge_video

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], ignore_unknown_options=True)

@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.option('--version', '-V', is_flag=True, help="Show current version")
@click.option('--update', '-U', is_flag=True, help="Update yuu to the newest version")
def cli(version=False, update=False):
    """
    A simple AbemaTV video downloader
    """
    if version:
        print('yuu rewrite v{} - Created by NoAiOne'.format(__version__))
        exit(0)
    if update:
        import sys
        print('[INFO] Updating yuu...'.format(ver=__version__))
        upstream_data = requests.get("https://pastebin.com/raw/Bt3ZLjfu").json()
        upstream_version = upstream_data['version']
        #upstream_change = upstream_data['changelog']
        if upstream_version == __version__:
            print('[INFO] Already on the newest version.')
            exit(0)
        print('[INFO] Updating to yuu version {} (Current: v{})'.format(upstream_version, __version__))

        if getattr(sys, "frozen", False):
            # It's from executable
            print('[INFO] There\'s currently no executeable release for yuu')
            exit(0)
        else:
            # It's from pip
            print('[WARN] To update yuu currently, use normal `pip install -U yuu=={}` command'.format(upstream_version))
            exit(1)


@cli.command("streams", short_help="Check supported website")
def streams_list():
    supported = {
        "AbemaTV": ["No", "No", "Yes (JP)"],
        "Aniplus Asia": ["Yes", "No", "Yes (SEA)"],
        "GYAO!": ["No", "No", "Yes (JP)"]
    }

    print('[INFO] Supported website')
    print('{0: <{width}}{1: <{width}}{2: <{width}}{3: <{width}}'.format("   Website", "Need Login?", "Premium Download?", "Proxy Needed?", width=18))
    for k, v_ in supported.items():
        log_, premi_, proxy_ = v_
        print('{0: <{width}}{1: <{width}}{2: <{width}}{3: <{width}}'.format('>> ' + k, log_, premi_, proxy_, width=18))


@cli.command("download", short_help="Download a video from yuu Supported we(e)bsite")
@click.argument("input", metavar="<URL site>")
@click.option("--username", "-U", required=False, default=None, help="Use username/password to download premium video")
@click.option("--password", "-P", required=False, default=None, help="Use username/password to download premium video")
@click.option("--proxy", "-p", required=False, default=None, metavar="<ip:port/url>", help="Use http(s)/socks5 proxies (please add `socks5://` if you use socks5)")
@click.option("--resolution", "-r", "res", required=False, default="best", help="Resolution to be downloaded (Default: best)")
@click.option("--resolutions", "-R", "resR", is_flag=True, help="Show available resolutions")
@click.option("--output", "-o", required=False, default=None, help="Output filename")
@click.option('--verbose', '-v', is_flag=True, help="Enable verbosity")
def main_downloader(input, username, password, proxy, res, resR, output, verbose):
    """
    Main command to access downloader
    
    Check supported streams for yuu: `yuu streams`
    """
    print('[INFO] Starting yuu rewrite v{ver}...'.format(ver=__version__))

    upstream_data = requests.get("https://pastebin.com/raw/Bt3ZLjfu").json()
    upstream_version = upstream_data['version']
    if upstream_version != __version__:
        print('[INFO] There\'s new version available to download, please update using `pip install yuu -U`.')
        exit(0)

    sesi = requests.Session()
    try:
        sesi.get('http://httpbin.org/get')
        pmode = "No proxy"
    except:
        print('[ERROR] No connection available to make requests')
        exit(1)

    if proxy:
        print('[INFO] Testing proxy')
        try:
            proxy_test = [
                {'http': proxy, 'https': proxy},
                {'https': proxy},
                {'http': proxy}
            ]
            for mode in proxy_test:
                try:
                    if verbose:
                        print('[DEBUG] Testing {x} mode proxy'.format(x="+".join(mode.keys())))
                    sesi.proxies = mode
                    sesi.get('http://httpbin.org/get') # Test website to check if proxy works or not
                    pmode = "+".join(mode.keys()).upper() + "/SOCKS5"
                    break
                except requests.exceptions.RequestException:
                    if verbose:
                        print('[DEBUG] Failed')
                    if mode == proxy_test[-1]:
                        print('[ERROR] Cannot connect to proxy (Request timeout)')
                        exit(1)
        except KeyboardInterrupt:
            print('[WARN] Interrupted')
            exit(0)
    if verbose:
        print('[DEBUG] Using proxy mode: {}'.format(pmode))

    yuuParser = get_parser(input)

    if not yuuParser:
        print('[ERROR] Unknown url format')
        exit(1)

    yuuParser = yuuParser(input, sesi, verbose)

    if yuuParser.authorization_required:
        if username is None and password is None:
            print('[WARN] You need to be logged in to use download from this VOD')
            exit(1)
        result, reason = yuuParser.authorize(username, password)
        if not result:
            print('[ERROR] {}: {}'.format(yuuParser.type, reason))
            exit(1)

    if username and password and not yuuParser.authorized:
        result, reason = yuuParser.authorize(username, password)
        if not result:
            print('[ERROR] {}: {}'.format(yuuParser.type, reason))
            exit(1)

    print('[INFO] {}: Fetching user token'.format(yuuParser.type))
    result, reason = yuuParser.get_token()
    if not result:
        print('[ERROR] {}: {}'.format(yuuParser.type, reason))
        exit(1)

    print('[INFO] {}: Parsing url'.format(yuuParser.type))
    output_name, reason = yuuParser.parse(res, resR)
    if not output_name:
        print('[ERROR] {}: {}'.format(yuuParser.type, reason))
        exit(1)
    if resR:
        print('[INFO] {}: Checking available resolution'.format(yuuParser.type))
        avares = yuuParser.resolutions()
        print('[INFO] {}: Available resolution:'.format(yuuParser.type))
        print('{0: <{width}}{1: <{width}}{2: <{width}}{3: <{width}}'.format("   Key", "Resolution", "Video Quality", "Audio Quality", width=16))
        for res in avares:
            r_c, wxh = res
            vidq, audq = yuuParser.resolution_data[r_c]
            print('{0: <{width}}{1: <{width}}{2: <{width}}{3: <{width}}'.format('>> ' + r_c, wxh, vidq, audq, width=16))
        exit(0)

    print('[INFO] {}: Parsing m3u8'.format(yuuParser.type))
    files, iv, reason = yuuParser.parse_m3u8()

    if not files:
        print('[ERROR] {}: {}'.format(yuuParser.type, reason))
        exit(1)

    if yuuParser.resolution != res and res not in ['best', 'worst']:
        print('[WARN] Resolution {} are not available'.format(res))
        print('[WARN] Switching to {}'.format(yuuParser.resolution))
        res = yuuParser.resolution

    output = yuuParser.check_output(output, output_name)

    illegalchar = ['/', '<', '>', ':', '"', '\\', '|', '?', '*'] # https://docs.microsoft.com/en-us/windows/desktop/FileIO/naming-a-file
    for char in illegalchar:
        output = output.replace(char, '_')

    print('[INFO] {}: Fetching video key'.format(yuuParser.type))
    video_key, reason = yuuParser.get_video_key()
    if not video_key:
        print('[ERROR] {}: {}'.format(yuuParser.type, reason))
        exit(1)

    print('[INFO][DOWN] Starting downloader...')
    print('[INFO][DOWN] Output: {}'.format(output))
    print('[INFO][DOWN] Resolution: {}'.format(yuuParser.resolution))
    print('[INFO][DOWN] Estimated file size: {} MiB'.format(yuuParser.est_filesize))

    # Initialize Download Process
    yuuDownloader = yuuParser.get_downloader(files, video_key, iv)
    if yuuDownloader.merge: # Workaround for stream that don't use .m3u8
        dl_list, temp_dir = yuuDownloader.download_chunk()
        if not dl_list:
            if temp_dir:
                shutil.rmtree(temp_dir)
            exit(1)
    else:
        yuuDownloader.download_chunk(output)
    if yuuDownloader.merge:
        print('[INFO][DOWN] Finished downloading')
        print('[INFO][DOWN] Merging video')
        merge_video(dl_list, output)
        shutil.rmtree(temp_dir)
    print('[INFO] Finished downloading: {}'.format(output))
    exit(0)


if __name__=='__main__':
    cli()
