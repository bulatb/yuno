from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
    name='Yuno',
    version='0.4',

    packages=find_packages() + ['resources'],
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'yuno = yuno.launch:main'
        ]
    }
)
