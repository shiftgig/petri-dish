#!/usr/bin/env python3

from setuptools import setup


def long_description():
    """
    Attempt to read README.rst (which is generated during deploy-time),
    otherwise, use README.md.
    """
    try:
        return open('README.rst').read()
    except IOError:
        return open('README.md').read()


setup(
    name='petri-dish',
    description='Build experiments spliting subjects into tratment groups',
    author='Hugo Osvaldo Barrera, Shiftgig Inc',
    author_email='hbarrera@shiftgig.com',
    url='https://github.com/sgrepo/petri-dish',
    license='ALv2',
    packages=['petri_dish'],
    include_package_data=True,
    install_requires=[
        'pandas',
        'gspread',
        'google-auth',
        'scipy',
        'psycopg2',
    ],
    long_description=long_description(),
    use_scm_version={
        'version_scheme': 'post-release',
        'write_to': 'petri_dish/version.py',
    },
    setup_requires=['setuptools_scm'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ]
)
