# yuu - Changelog

[![koito yuu](https://p.n4o.xyz/i/fzpt7mt.jpg)](https://anilist.co/character/123528/Yuu-Koito)

[![pypi version](https://img.shields.io/pypi/v/yuu.svg?style=for-the-badge)](https://pypi.org/project/yuu/) [![python version](https://img.shields.io/pypi/pyversions/yuu.svg?style=for-the-badge)](#) [![License](https://img.shields.io/github/license/noaione/yuu.svg?style=for-the-badge)](https://github.com/noaione/yuu/blob/master/LICENSE)

### Version 0.1
- First release

#### Version 0.1.1
- Add proxy mode
- Using session
- Fix some problem

#### Version 0.1.2
- Added more proxy test
- Add verbose
- Fix more problem

#### Version 0.1.2.1
- Proxy test fix

#### Version 0.1.2.2
- Variable change
- More verbose

#### Version 0.1.2.3
- Fixes decryptData() problem (Issue #1)

#### Version 0.1.3
- Fix output override problem

#### Version 0.1.4
- Change webparse() from using beautifulsoup4 to json API
- Rearrange code in `command.py`

#### Version 0.1.4.1
- Added some support for `channel` or `slots` url things
- Make some auto-output-parser thingy for direct m3u8 link
- Cleaning some code

#### Version 0.1.4.2
- Add Illegal/Forbidden character replacer

#### Version 0.1.5
- Tabs -> Spaces Indentation
- Add `--resolutions` for showing list of available resolution
- Some fixes for the API changes

### Version 0.2.0
- Change from argparse to click for commands parsing
- Add updater to make sure people using the newest version
- Fix some check
- Add an error handling if the video cannot be downloaded
- Cleaning the code

#### Version 0.2.1
- Make a proper error message
- Add KeyboardInterrupt Handler while downloading, so it will delete the temporary folder
- Made updater a little bit nicer (Added changelog to the output)
- Add more information to `--resolutions` option

#### Version 0.2.2
- Fix updater

#### Version 0.2.3
- Fix runAsAdmin

### Version 1.0.0
- (Almost) Full rewrite!
- Add support for some website (Abema, Aniplus, GYAO!)
- Add support for easy additional new website support
- More on the changes from commit [`1f472c3`](https://github.com/noaione/yuu/commit/1f472c306e71af4ca5ee6c68d84fb296a347615a) to [`202532a`](https://github.com/noaione/yuu/commit/202532ad767306dd4096c6c5a9114c10f04def1a)

### Version 1.1.0
- Add muxing support
- Add support for AbemaTV Premium Video
- Some bug fixing that I don't even know if it's even fixed.
- Removed `legacy` branch link

### Version 1.2.0
- Add support for series/playlist download (batch download) [Currently only for Abema]
- Removed old and unused code
- Now using logger/logging (As suggested by *someone*)
- Grammar fix

#### Version 1.2.1
- Use mkvmerge and ffmpeg as fallback
- Add missing `None`
- Fix Abema wrong resolution filename
