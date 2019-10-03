# (koito) yuu 
A simple AbemaTV and other we(e)bsite video downloader in python

Old version/legacy mode: [legacy branch](https://github.com/noaione/yuu/tree/legacy)

[![koito yuu](https://p.n4o.xyz/i/fzpt7mt.jpg)](https://anilist.co/character/123528/Yuu-Koito)

[![pypi version](https://img.shields.io/pypi/v/yuu.svg?style=for-the-badge)](https://pypi.org/project/yuu/) [![python version](https://img.shields.io/pypi/pyversions/yuu.svg?style=for-the-badge)](#) [![License](https://img.shields.io/github/license/noaione/yuu.svg?style=for-the-badge)](https://github.com/noaione/yuu/blob/master/LICENSE)

## Requirements
- click
- pycryptodome
- Python 3.5+
- m3u8
- tqdm
- Japan connection/proxy/vpn

## Supported web
- AbemaTV
- Aniplus Asia
- GYAO!

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
  download  Download a video from yuu Supported we(e)bsite
  streams   Check supported website

///////////////////////////////////////////////////
>> yuu download -h
Usage: yuu download [OPTIONS] <URL site>

  Main command to access downloader

  Check supported streams for yuu: `yuu streams`

Options:
  -U, --username TEXT        Use username/password to download premium video
  -P, --password TEXT        Use username/password to download premium video
  -p, --proxy <ip:port/url>  Use http(s)/socks5 proxies (please add
                             `socks5://` if you use socks5)
  -r, --resolution TEXT      Resolution to be downloaded (Default: best)
  -R, --resolutions          Show available resolutions
  -o, --output TEXT          Output filename
  -v, --verbose              Enable verbosity
  -h, --help                 Show this message and exit.
```

- **`--username/-U`**: Use yuu with registered username/password
- **`--password/-P`**: Use yuu with registered username/password
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
