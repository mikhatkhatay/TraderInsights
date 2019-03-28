# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 22:03:53 2019

@author: M. Ibrahim
"""

from setuptools import find_packages, setup

setup(
    name='TraderInsights',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask', 'wtforms'
    ],
)