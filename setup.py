#!/usr/bin/env python
import os
from setuptools import setup, find_packages


long_description = open(
    os.path.join(
        os.path.dirname(__file__),
        'README.rst'
    )
).read()


setup(
    name='dimsum',
    author='Apurba Nath',
    version='0.1',
    license='LICENSE',
    url='https://github.com/sans-sense/dimsum',
    description='Dysfuncational alternate way of machine learning',
    long_description=long_description,
    packages=find_packages('.'),
    install_requires = [
    ],
    entry_points={
        'console_scripts': [
            'dimsum = dimsum.entry_points.run_dimsum:run',
        ]
    },
)
