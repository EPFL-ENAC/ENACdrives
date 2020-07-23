#!/usr/bin/env python3
# Bancal Samuel

from enacdrives import utility
from distutils.core import setup

setup(
    name='ENACdrives',
    version=utility.CONST.VERSION,
    description='Access your Network Drives easily.',
    long_description='Access your Network Drives easily.',
    author='Samuel Bancal',
    author_email='Samuel.Bancal@epfl.ch',
    url='https://enacit.epfl.ch/enacdrives/',
    packages=['enacdrives'],
    scripts=[
        'bin/enacdrives',
    ],
    data_files=[
        ('share/applications', ['meta/enacdrives.desktop']),
        ('share/pixmaps',
            ['pixmaps/bookmark_off.png',
             'pixmaps/bookmark_on.png',
             'pixmaps/critical_48.png',
             'pixmaps/enacdrives.icns',
             'pixmaps/enacdrives.ico',
             'pixmaps/enacdrives.png',
             'pixmaps/info_48.png',
             'pixmaps/mounted.png',
             'pixmaps/msg_48.png',
             'pixmaps/umounted.png',
             'pixmaps/warning_48.png',
             'pixmaps/warning.png']),
        # ('share/man/man1', ['man/hello.1']),
    ],
    classifiers=[
        'Development Status :: 6 - Mature',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'License :: Free To Use But Restricted',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],
    platforms='POSIX',
    license='MIT License',
)
