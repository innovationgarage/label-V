#!/usr/bin/env python

import setuptools

setuptools.setup(name='label-V',
      version='0.1',
      description='video annotation tool',
      author='Saghar Asadi',
      author_email='saghar@innovationgarage.no',
      url='https://github.com/innovationgarage/label-V',
      packages=setuptools.find_packages(),
      install_requires=[
          'numpy',
          'cv2'
      ],
      include_package_data=True,
      entry_points='''
      [console_scripts]
      labelv = labelv:main
      '''
  )

