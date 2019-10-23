import json
import os
import re
import subprocess

from tqdm import tqdm

from .ext import *

__version__ = "1.0.0"


def get_parser(url):
    """
    Function that are called first time to check if it's a valid supported link

    :return: A class of one of supported website
    """
    valid_abema = r'http(?:|s)://(?:abema\.tv)/(?:channels|video)/(?:\w*)(?:/|-\w*/)((?P<slot>slots/)|)(?P<video_id>.*[^-_])'
    valid_gyao = r'(?isx)http(?:|s)://gyao.yahoo.co.jp/(?:player|p|title[\w])/(?P<p1>[\w]*.*)'
    valid_aniplus = r'http(?:|s)://(?:www\.|)aniplus-asia\.com/episode/(?P<video_id>[\w]*.*)'
    if re.match(valid_abema, url):
        return AbemaTV
    elif re.match(valid_gyao, url):
        return GYAO
    elif re.match(valid_aniplus, url):
        return Aniplus
    return None


def merge_video(path, output):
    """
    Merge every video chunk to a single file output
    """
    with open(output, 'wb') as out:
        with tqdm(total=len(path), desc="Merging", ascii=True, unit="file") as pbar:
            for i in path:
                out.write(open(i, 'rb').read())
                os.remove(i)
                pbar.update()


def mux_video(old_file):
    """
    Mux .ts or .mp4 or anything to a .mkv

    It will try to use ffmpeg first, if it's not in the PATH, then it will try to use mkvmerge
    If it's doesn't exist too, it just gonna skip.
    """
    # FFMPEG check
    use_ffmpeg = False
    use_mkvmerge = False
    try:
        subprocess.check_call(['ffmpeg', '-version'])
        use_ffmpeg = True
    except FileNotFoundError:
        try:
            subprocess.check_call(['mkvmerge', '-V'])
            use_mkvmerge = True
        except FileNotFoundError:
            return None

    fn_, _ = os.path.splitext(old_file)
    if use_ffmpeg:
        subprocess.call(['ffmpeg', '-i', old_file, '-c', 'copy', '{f}.mkv'.format(f=fn_)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if use_mkvmerge:
        subprocess.call(['mkvmerge', '-o', '{f}.mkv'.format(f=fn_), old_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return '{f}.mkv'.format(f=fn_)


def _prepare_yuu_data():
    if os.name == "nt":
        yuu_folder = os.path.join(os.getenv('LOCALAPPDATA'), 'yuu_data')
    else:
        yuu_folder = os.path.join(os.getenv('HOME'), '.yuu_data')
    if not os.path.isdir(yuu_folder):
        os.mkdir(yuu_folder)

    if not os.path.isfile(os.path.join(yuu_folder, 'yuu_download.json')):
        with open(os.path.join(yuu_folder, 'yuu_download.json'), 'w') as f:
            json.dump({}, f)
