from setuptools import setup, find_packages
import sys, os

version = '0.0'

requires = [
    'pymongo',
    'mock'
]

test_requires = ['mock']

setup(name='maxflip',
      version=version,
      description="Max database migration runner",
      long_description="""\
A tool to make migrations or massive modifications to a max database""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Carles Bruguera',
      author_email='carles.bruguera@upcnet.es',
      url='https://github.com/UPCnet/maxflip',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      tests_require=requires + test_requires,
      test_suite="maxflip.tests",
      install_requires=requires,
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
