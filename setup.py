#!/home/david/.conda/envs/intensity/bin/python

from setuptools import setup, find_packages

setup(name='melee-env',
      version='0.4.0',
      description="Melee Bot",
      author="David Jones",
      author_email="d.t.jones@outlook.com",
      url="https://github.com/davdtjones/melee-env",
      install_requires=[
            'melee',
            'numpy',
            'requests'
      ],
      packages=find_packages()
      )

