"""
Flask-Negotiation
==================

Provides better content negotiation for flask.  
"""
from setuptools import setup
import setuptools

requires = [
    'Flask',
]

setup(
    name='Flask-Negotiation',
    version='0.1.0',
    url='http://blog.hardtack.me/',
    author='GunWoo Choi',
    author_email='6566gun@gmail.com',
    description='Better content negotiation for flask',
    long_description=__doc__,
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=requires,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
    ],
)
