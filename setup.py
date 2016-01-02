from setuptools import setup, find_packages

setup(
  name = 'bustime',
  version = '0.2.0',
  packages = find_packages(),
  description = 'SDK for the MTA Bus Time API',
  install_requires = ['requests>=2.0'],
  author = 'Steve Davis',
  author_email = 'steve@celery.club',
  url = 'https://github.com/celeryclub/bustime',
  download_url = 'https://github.com/celeryclub/bustime/tarball/0.2.0',
  keywords = 'mta bustime',
)
