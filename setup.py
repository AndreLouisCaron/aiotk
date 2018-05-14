# -*- coding: utf-8 -*-


from setuptools import find_packages, setup


def readfile(path):
    with open(path, 'rb') as stream:
        return stream.read().decode('utf-8')


version = readfile('src/aiotk/version.txt').strip()
readme = readfile('README.rst')


setup(
    name='aiotk',
    maintainer='Andre Caron',
    maintainer_email='andre.l.caron@gmail.com',
    version=version,
    url='https://github.com/AndreLouisCaron/aiotk',
    packages=find_packages(where='src'),
    package_dir={
        '': 'src',
    },
    package_data={
        'aiotk': [
            'version.txt',
        ],
    },
    long_description=readme,
    install_requires = [
        'typing-extensions>=3.6.5',
    ],
)
