#!/usr/bin/env python

import setuptools

setuptools.setup(name='labelv',
      version='0.1',
      description='label-v video frame labeler',
      author='Saghar Asadi',
      author_email='saghar@innovationgarage.no',
      url='https://github.com/innovationgarage/label-V',
      packages=setuptools.find_packages(),
      install_requires=[
          "numpy==1.13.3",
          "opencv-contrib-python==3.3.0.10",
          "scipy==1.0.0",
          "sk-video==1.1.8",
          "Flask==1.0"
      ],
      include_package_data=True,
      entry_points='''
      [console_scripts]
      labelv = labelv.labelv:labelv
      labelv-service = labelv.service:main
      '''
  )
