#!/usr/bin/env python3

import setuptools

setuptools.setup(
    name='axel',
    version='0.1',
    description='Automated media handling, placement, and organization',
    author='Craig Cabrey',
    author_email='craigcabrey@gmail.com',
    url='http://github.com/craigcabrey/axel',
    license='MIT',
    py_modules=['axel'],
    scripts=['axelctl'],
    install_requires=[
		'guessit>=0.1.12',
		'pushbullet.py>=0.10.0',
		'transmissionrpc>=0.11',
		'unrar>=0.3'
	],
    long_description=open('README.md').read(),
    packages=['axel'],
    package_dir={
        'axel': 'axel'
    }
)
