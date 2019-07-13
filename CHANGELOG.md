# yuu - Changelog

[![koito yuu](https://raw.githubusercontent.com/noaione/cdn/gh-pages/i/fzpt7mt.jpg)](https://anilist.co/character/123528/Yuu-Koito)

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
- Add a error handling if the video cannot be dowwnloaded
- Cleaning the code

#### Version 0.2.1
- Make a proper error message
- Add KeyboardInterrupt Handler while downloading, so it will delete the temporary folder
- Made updater a little bit nicer (Added changelog to the output)
- Add more information to `--resolutions` option

#### Version 0.2.2
- Fix updater