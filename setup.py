import setuptools
from yuu.common import __version__

setuptools.setup(name = 'yuu',
version = __version__,
description = 'Yuu - A simple AbemaTV video ripper',
author = 'noaione',
author_email = 'noaione0809@gmail.com',
keywords = ['ripping', 'downloader', 'parser'],
license = 'GNU GPLv3',
url = 'https://github.com/noaione/yuu',
packages = setuptools.find_packages(),
install_requires = ['requests[socks]', 'm3u8', 'tqdm', 'pycryptodome'],
classifiers = ['Development Status :: 5 - Production/Stable', 'License :: OSI Approved :: GNU GPLv3 License', 'Programming Language :: Python :: 3', 'Programming Language :: Python :: 3.5', 'Programming Language :: Python :: 3.6', 'Programming Language :: Python :: 3.7'],
entry_points = {
    'console_scripts': ['yuu=yuu.command:main']
})