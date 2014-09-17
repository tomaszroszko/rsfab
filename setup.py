#! /usr/bin/env python
from distutils.core import setup
import sys

reload(sys).setdefaultencoding('Utf-8')

setup(
    name='rsfab',
    version='2.1.1',
    author='Tomasz Roszko',
    author_email='tomaszroszko@gmail.com',
    description='Helper functions for fabric',
    long_description=open('README.md').read(),
    url='https://github.com/tomaszroszko/rsfab',
    license='BSD License',
    platforms=['OS Independent'],
    packages=['rsfab'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 2.1.0 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Documentation',
    ],
)
