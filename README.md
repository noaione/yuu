# yuu 
A simple AbemaTV video ripper in python

## Requirements
- pycryptodome
- Python 3.5+
- m3u8
- tqdm
- BeautifulSoup4
- Japan connection/proxy/vpn

## Installation
`pip install yuu`
or clone this project and type `pip install .`

## Usage
```
usage: yuu [-h] [--proxies PROXY]
           [--resolution {180p,240p,360p,480p,720p,1080p}] [--output OUTPUT]
           [--version]
           input

A simple AbemaTV video ripper

positional arguments:
  input                 AbemaTV url site or m3u8

optional arguments:
  -h, --help            show this help message and exit
  --proxies PROXY, -p PROXY
                        Use http(s)/socks5 proxies (please add `socks5://` if
                        you use socks5)
  --resolution {180p,240p,360p,480p,720p,1080p}, -r {180p,240p,360p,480p,720p,1080p}
                        Resolution (Default: 1080p)
  --output OUTPUT, -o OUTPUT
                        Output filename
  --version, -v         show program's version number and exit

Created by NoAiOne - Version x.x
```

**Warning: I still haven't tested this program with proxy completely**

Example command: 
- >`yuu https://abema.tv/video/episode/189-11_s1_p1`
    Download 1080p video of Go-Toubun no Hanayome episode 01
- >`yuu https://abema.tv/video/episode/189-11_s1_p1 -r 480p`
    Download 480p video of Go-Toubun no Hanayome episode 01
- >`yuu https://ds-vod-abematv.akamaized.net/program/189-11_s1_p1/1080/playlist.m3u8 -o '5toubun01.ts'`
    Download 1080p video from m3u8 link
- >`yuu https://abema.tv/video/episode/189-11_s1_p1 -p '127.0.0.1:3128`
    Download 480p video of Go-Toubun no Hanayome episode 01 using 127.0.0.1:3128 proxy

## Credits
- jackyzy823 (Decryption key fetching method)
- Last-Order ([Minyami](https://github.com/Last-Order/minyami) author)

This project are protected by GNU General Public License v3