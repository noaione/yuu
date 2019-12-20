import logging
import os
import shutil
import subprocess
from datetime import datetime

import click
import requests

from .common import (__version__, _prepare_yuu_data, get_parser,
                     get_yuu_folder, merge_video, mux_video, version_compare)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], ignore_unknown_options=True)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-1s -- [%(levelname)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='{f}/yuu_log-{t}.log'.format(f=get_yuu_folder(), t=datetime.today().strftime("%Y-%m-%d_%HH%MM%SS")),
                    filemode='w')

yuu_logger = yuu_logger.getLogger('yuu')


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.option('--version', '-V', is_flag=True, help="Show current version")
def cli(version=False):
    """
    A simple AbemaTV and other we(e)bsite video downloader
    """
    if version:
        print('yuu v{} - Created by NoAiOne'.format(__version__))
        exit(0)


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
@click.option("--mux", is_flag=True, help="Mux .ts to .mkv (Need ffmpeg or mkvmerge)")
@click.option("--keep-fragments", "-keep", "keep_", is_flag=True, help="Keep downloaded fragment and combined fragment (If muxing) (Default: no)")
@click.option("--output", "-o", required=False, default=None, help="Output filename")
@click.option('--verbose', '-v', is_flag=True, help="Enable verbosity")
def main_downloader(input, username, password, proxy, res, resR, mux, keep_, output, verbose):
    """
    Main command to access downloader
    
    Check supported streams from yuu with `yuu streams`
    """
    console = logging.StreamHandler()
    LOG_LEVEL = logging.INFO
    if verbose:
        LOG_LEVEL = logging.DEBUG
    console.setLevel(LOG_LEVEL)
    formatter1 = logging.Formatter('[%(levelname)s] %(message)s')
    console.setFormatter(formatter1)
    yuu_logger.addHandler(console)

    yuu_logger.info('Starting yuu v{ver}...'.format(ver=__version__))

    upstream_data = requests.get("https://pastebin.com/raw/Bt3ZLjfu").json()
    upstream_version = upstream_data['version']
    if version_compare(upstream_version) > 0:
        yuu_logger.info('There\'s new version available to download, please update using `pip install yuu=={nv} -U`.'.format(nv=upstream_version))
        yuu_logger.log(0, '====== Changelog v{} ======'.format(upstream_version))
        yuu_logger.log(0, upstream_data['changelog'])
        print('====== Changelog v{} ======'.format(upstream_version))
        print(upstream_data['changelog'])
        exit(0)

    sesi = requests.Session()

    if proxy:
        sesi.proxies = {'http': proxy, 'https': proxy}
    yuu_logger.debug('Using proxy: {}'.format(proxy))

    _prepare_yuu_data() # Prepare yuu_download.json
    yuuParser = get_parser(input)

    if not yuuParser:
        yuu_logger.error('Unknown url format')
        exit(1)

    yuuParser = yuuParser(input, sesi)
    formatter3 = logging.Formatter('[%(levelname)s] {}: %(message)s'.format(yuuParser.type))
    yuu_logger.removeHandler(console)
    console.setFormatter(formatter3)
    yuu_logger.addHandler(console)

    if yuuParser.authorization_required:
        if username is None and password is None:
            yuu_logger.warning('You need to be logged in to use download from this VOD')
            exit(1)
        yuu_logger.info('Authenticating')
        result, reason = yuuParser.authorize(username, password)
        if not result:
            yuu_logger.error('{}'.format(reason))
            exit(1)
    if username and password and not yuuParser.authorized:
        yuu_logger.info('Authenticating')
        result, reason = yuuParser.authorize(username, password)
        if not result:
            yuu_logger.error('{}'.format(reason))
            exit(1)

    if not yuuParser.authorized:
        yuu_logger.info('Fetching temporary user token'.format(yuuParser.type))
        result, reason = yuuParser.get_token()
        if not result:
            yuu_logger.error('{}'.format(reason))
            exit(1)

    yuu_logger.info('Parsing url'.format(yuuParser.type))
    output_name, reason = yuuParser.parse(res, resR)
    if not output_name:
        yuu_logger.error('{}'.format(reason))
        exit(1)
    if resR:
        yuu_logger.info('Checking available resolution'.format(yuuParser.type))
        avares, reason = yuuParser.resolutions()
        if not avares:
            yuu_logger.error('{}'.format(reason))
            exit(1)
        yuu_logger.info('Available resolution:'.format(yuuParser.type))
        yuu_logger.log('{0: <{width}}{1: <{width}}{2: <{width}}{3: <{width}}'.format("   Key", "Resolution", "Video Quality", "Audio Quality", width=16))
        print('{0: <{width}}{1: <{width}}{2: <{width}}{3: <{width}}'.format("   Key", "Resolution", "Video Quality", "Audio Quality", width=16))
        for res in avares:
            r_c, wxh = res
            vidq, audq = yuuParser.resolution_data[r_c]
            yuu_logger.log('{0: <{width}}{1: <{width}}{2: <{width}}{3: <{width}}'.format('>> ' + r_c, wxh, vidq, audq, width=16))
            print('{0: <{width}}{1: <{width}}{2: <{width}}{3: <{width}}'.format('>> ' + r_c, wxh, vidq, audq, width=16))
        exit(0)

    yuu_logger.info('Parsing m3u8'.format(yuuParser.type))
    files, iv, reason = yuuParser.parse_m3u8()

    if not files:
        yuu_logger.error('{}'.format(reason))
        exit(1)

    if yuuParser.resolution != res and res not in ['best', 'worst']:
        yuu_logger.warn('Resolution {} are not available'.format(res))
        yuu_logger.warn('Switching to {}'.format(yuuParser.resolution))
        res = yuuParser.resolution

    output = yuuParser.check_output(output, output_name)

    illegalchar = ['/', '<', '>', ':', '"', '\\', '|', '?', '*'] # https://docs.microsoft.com/en-us/windows/desktop/FileIO/naming-a-file
    for char in illegalchar:
        output = output.replace(char, '_')

    yuu_logger.info('Fetching video key'.format(yuuParser.type))
    video_key, reason = yuuParser.get_video_key()
    if not video_key:
        yuu_logger.error('{}'.format(reason))
        exit(1)

    formatter2 = logging.Formatter('[%(levelname)s][DOWN] %(message)s')
    yuu_logger.removeHandler(console)
    console.setFormatter(formatter2)
    yuu_logger.addHandler(console)

    yuu_logger.info('Starting downloader...')
    yuu_logger.info('Output: {}'.format(output))
    yuu_logger.info('Resolution: {}'.format(yuuParser.resolution))
    yuu_logger.info('Estimated file size: {} MiB'.format(yuuParser.est_filesize))

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
        if mux:
            yuu_logger.info('Muxing video\n')
            mux_video(output)
    if yuuDownloader.merge:
        yuu_logger.info('Finished downloading')
        yuu_logger.info('Merging video')
        merge_video(dl_list, output)
        if not keep_:
            shutil.rmtree(temp_dir)
    if mux:
        if os.path.isfile(output):
            yuu_logger.info('Muxing video\n')
            result = mux_video(output)
            if not result:
                yuu_logger.warn('There\'s no available muxers that can be used, skipping...')
            elif result and os.path.isfile(result):
                if not keep_:
                    os.remove(output)
            output = result
    yuu_logger.info('Finished downloading: {}'.format(output))
    exit(0)


if __name__=='__main__':
    cli()
