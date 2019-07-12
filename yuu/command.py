import click
import shutil
import requests
import subprocess

from .downloader import get_video, merge_video
from .parser import webparse, webparse_m3u8, parsem3u8, fetch_video_key, get_auth_token, available_resolution
from .common import res_data, __version__

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
            subprocess.check_call('pip install -U yuu=={}'.format(upstream_version))
        except subprocess.CalledProcessError:
            print('[ERROR] Updater returned non-zero exit code')
            exit(1)
        print('\n=== yuu version {} changelog ==='.format(upstream_version))
        print(upstream_change+'\n')
        print('[INFO] Updated.')
        exit(0)


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

    upstream_data = requests.get("https://pastebin.com/raw/Bt3ZLjfu").json()
    upstream_version = upstream_data['version']
    if upstream_version != __version__:
        print('[INFO] There\'s new version available to download, please update using `yuu -U`.')
        exit(0)

    sesi = requests.Session()
    if proxy:
        print('[INFO] Testing proxy')
        sesi.proxies = {'http': proxy, 'https': proxy}
        # Somebody tell me how to do recursive test properly
        try:
            if verbose:
                print('[DEBUG] Testing http+https mode proxy')
            sesi.get('http://httpbin.org/get') # Some test website to check if proxy works or not
            pmode = "HTTP+HTTPS/SOCKS5"
        except requests.exceptions.RequestException:
            if verbose:
                print('[DEBUG] Failed')
            sesi = requests.Session()
            sesi.proxies = {'http': proxy}
            try:
                if verbose:
                    print('[DEBUG] Testing http mode proxy')
                sesi.get('http://httpbin.org/get') # This too but in https mode
                pmode = "HTTP/SOCKS5"
            except requests.exceptions.RequestException:
                if verbose:
                    print('[DEBUG] Failed')
                sesi = requests.Session()
                sesi.proxies = {'https': proxy} # Final test if it's failed then it will return error
                try:
                    if verbose:
                        print('[DEBUG] Testing https mode proxy')
                    sesi.get('http://httpbin.org/get')
                    pmode = "HTTPS/SOCKS5"
                except requests.exceptions.RequestException:
                    if verbose:
                        print('[DEBUG] Failed')
                    print('[ERROR] Cannot connect to proxy (Request timeout)')
                    exit(1)
    try:
        sesi.get('http://httpbin.org/get')
        pmode = "No proxy"
    except:
        print('[ERROR] No connection available to make requests')
        exit(1)
    if verbose:
        print('[DEBUG] Using proxy mode: {}'.format(pmode))

    print('[INFO] Fetching user token')
    authtoken = get_auth_token(sesi, verbose)
    sesi.headers.update({'Authorization': authtoken[0]})

    if input[-5:] != '.m3u8':
        print('[INFO] Parsing webpage')
        outputtitle, m3u8link = webparse(input, res, sesi, verbose)
        if resR:
            print('[INFO] Checking available resolution')
            avares = available_resolution(m3u8link, sesi, verbose)
            print('[INFO] Available resolution:')
            print('{0: <{width}}{1: <{width}}{2: <{width}}{3: <{width}}'.format("", "Resolution", "Video Quality", "Audio Quality", width=16))
            for res in avares:
                r_c, wxh = res
                vidq, audq = res_data[r_c]
                print('{0: <{width}}{1: <{width}}{2: <{width}}{3: <{width}}'.format('>> ' + r_c, wxh, vidq, audq, width=16))
            exit(0)
        print('[INFO] Parsing m3u8')
        files, iv, ticket = parsem3u8(m3u8link, res, sesi, verbose)
        if output:
            if output[-3:] == '.ts':
                output = output
            else:
                output = output + '.ts'
        else:
            output = '{x} (AbemaTV {r}).ts'.format(x=outputtitle, r=res)
        if verbose:
            print('[DEBUG] Output file: {}'.format(output))
    else:
        print('[INFO] Parsing m3u8')
        outputtitle, res = webparse_m3u8(input, sesi, verbose)
        files, iv, ticket = parsem3u8(input, res, sesi, verbose)
        if output:
            if output[-3:] == '.ts':
                output = output
            else:
                output = output + '.ts'
        else:
            output = '{x} (AbemaTV {r}).ts'.format(x=outputtitle, r=res)

    # Don't use forbidden/illegal character (replace it with underscore)
    illegalchar = ['/', '<', '>', ':', '"', '\\', '|', '?', '*'] # https://docs.microsoft.com/en-us/windows/desktop/FileIO/naming-a-file
    for char in illegalchar:
        output = output.replace(char, '_')

    print('[INFO] Fetching video key')
    getkey = fetch_video_key(ticket, authtoken, sesi, verbose)
    
    print('[INFO][DOWN] Starting downloader...')
    print('[INFO][DOWN] Resolution: {}'.format(res))
    dllist, tempdir = get_video(files, getkey, iv, sesi, verbose)
    if not dllist:
        if tempdir:
            shutil.rmtree(tempdir)
        exit(0)
    print('[INFO][DOWN] Finished downloading')
    print('[INFO] Merging video')
    merge_video(dllist, output)

    print('[INFO] Cleaning up')
    shutil.rmtree(tempdir)
    exit(0)


def main():
    cli()


if __name__=='__main__':
    cli()
