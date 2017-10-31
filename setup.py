#!/usr/bin/env python
from distutils.core import setup

setup(
    name='label-V',
    version='0.1',
    description='video annotation tool',
    author='Saghar Asadi',
    author_email='saghar@innovationgarage.no',
    url='https://github.com/innovationgarage/label-V',
    py_modules=['labelv'],
    classifiers=[
        # "opencv-python",
        # "opencv-contrib-python",
        "argparse",
        "numpy",
    ],
    entry_points='''
    [console_scripts]
    labelv = labelv:main
    '''
)

