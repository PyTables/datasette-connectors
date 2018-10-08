from setuptools import setup
import os

def get_version():
    with open('VERSION') as fd:
        return fd.read().strip()

def get_long_description():
    with open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'README.md'
    ), encoding='utf8') as fp:
        return fp.read()


setup(
    name='datasette-connectors',
    version=get_version(),
    description='Datasette support to other database types',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Javier Sancho',
    url='https://github.com/pytables/datasette-connectors',
    license='Apache License, Version 2.0',
    packages=['datasette_connectors'],
    install_requires=['datasette==0.25'],
    tests_require=['pytest', 'aiohttp'],
    entry_points='''
        [console_scripts]
        datasette=datasette_connectors.cli:cli
    '''
)
