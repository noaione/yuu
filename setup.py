import setuptools
from yuu.common import __version__

with open('README.md', 'r') as f:
    desc = f.read()

setuptools.setup(
    name = 'yuu',
    version = __version__,
    description = 'Yuu - A simple AbemaTV video downloader',
    long_description = desc,
    long_description_content_type = "text/markdown",
    author = 'noaione',
    author_email = 'noaione0809@gmail.com',
    keywords = [
        'ripping', 
        'downloader', 
        'parser'
    ],
    license = 'BSD-3-Clause',
    url = 'https://github.com/noaione/yuu',
    packages = setuptools.find_packages(),
    install_requires = [
        'requests[socks]', 
        'm3u8', 
        'tqdm', 
        'pycryptodome',
        'click'
    ],
    classifiers = [
        'Development Status :: 5 - Production/Stable', 
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3', 
        'Programming Language :: Python :: 3.5', 
        'Programming Language :: Python :: 3.6', 
        'Programming Language :: Python :: 3.7'
    ],
    entry_points = {
        'console_scripts': ['yuu=yuu.command:cli']
    }
)