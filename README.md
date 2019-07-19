# (koito) yuu 
A simple AbemaTV and other video downloader in python

## THIS IS A REWRITE VERISON
Current deployed version are at [master branch](https://github.com/noaione/yuu/tree/master)
To install this version: `pip install git+https://github.com/noaione/yuu.git@rewrite`

This version will add more website.
Currently need help:
- bilibili (Probably I will do it myself.)
- Ponimu (Need help figuring out some encryption [Read Here for more info.](https://github.com/noaione/yuu/blob/rewrite/yuu/ext/ponimu.py))

[![koito yuu](https://p.n4o.xyz/i/fzpt7mt.jpg)](https://anilist.co/character/123528/Yuu-Koito)

[![pypi version](https://img.shields.io/pypi/v/yuu.svg?style=for-the-badge)](https://pypi.org/project/yuu/) [![python version](https://img.shields.io/pypi/pyversions/yuu.svg?style=for-the-badge)](#) [![License](https://img.shields.io/github/license/noaione/yuu.svg?style=for-the-badge)](https://github.com/noaione/yuu/blob/master/LICENSE)

## Requirements
- click
- pycryptodome
- Python 3.5+
- m3u8
- tqdm
- Japan connection/proxy/vpn

## Installation
`pip install yuu`

or clone this project and type `pip install .`

## Usage
```
>> yuu -h
Usage: yuu [OPTIONS] COMMAND [ARGS]...

  A simple AbemaTV video downloader

Options:
  -V, --version  Show current version
  -U, --update   Update yuu to the newest version
  -h, --help     Show this message and exit.

Commands:
  download  Download video from abema.tv

///////////////////////////////////////////////////
>> yuu download -h
Usage: yuu download [OPTIONS] <AbemaTV url site or m3u8>

  Download a free video from abema

Options:
  -p, --proxy <ip:port/url>       Use http(s)/socks5 proxies (please add
                                  `socks5://` if you use socks5)
  -r, --resolution [180p|240p|360p|480p|720p|1080p]
                                  Resolution to be downloaded (Default: 1080p)
  -R, --resolutions               Show available resolutions
  -o, --output TEXT               Output filename
  -v, --verbose                   Enable verbosity
  -h, --help                      Show this message and exit.
```

- **`--proxies/-p`**: Download using proxy for people outside Japan
    - Example: `127.0.0.1:1080`, `http://127.0.0.1:1080`, `http://user:pass@127.0.0.1:1080`, `socks5://127.0.0.1:1080`
- **`--resolution/-r`**: Target resolution
- **`--resolutions/-R`**: Show available resolution
- **`--output/-o`**: Output filename (Automated if there's nothing omitted)
- **`--version/-V`**: Show version number
- **`--verbose/-v`**: Enable verbose/debug mode

**Information: Please use HTTPS proxy for now, it tested and works. SOCKS5 are not tested yet and HTTP doesn't work**

Example command: 
- >`yuu download -R https://abema.tv/video/episode/54-25_s1_p1`

    Show available resolution for `Yagate Kimi ni Naru` episode 01
- >`yuu download https://abema.tv/video/episode/54-25_s1_p1`

    Download 1080p video of `Yagate Kimi ni Naru` episode 01
- >`yuu download https://abema.tv/video/episode/54-25_s1_p1 -r 480p`

    Download 480p video of `Yagate Kimi ni Naru` episode 01
- >`yuu download https://ds-vod-abematv.akamaized.net/program/54-25_s1_p1/1080/playlist.m3u8 -o '5toubun01.ts'`

    Download 1080p video from m3u8 link
- >`yuu download https://abema.tv/video/episode/54-25_s1_p1 -p '127.0.0.1:3128`

    Download 480p video of `Yagate Kimi ni Naru` episode 01 using 127.0.0.1:3128 proxy

## Credits
- jackyzy823 (Decryption key fetching method)
- Last-Order ([Minyami](https://github.com/Last-Order/Minyami) author)

*This project are protected by BSD 3-Clause License*
