from setuptools import setup, find_packages

long_description = open('README.md').read()

setup(
    name='tm-editor',
    version='0.10.0',
    description="CMS Level-1 Trigger Menu Editor",
    long_description=long_description,
    author = "Bernhard Arnold",
    author_email = "bernhard.arnold@cern.ch",
    url = "http://globaltrigger.hephy.at/upgrade/tme",
    packages = find_packages(),
    install_requires=[
        'tm-table>=0.7.3',
        'tm-grammar>=0.7.3',
        'tm-eventsetup>=0.7.3',
        'PyQt5>=5.13'
    ],
    entry_points={
        'console_scripts': [
            'tm-editor = tmEditor.__main__:main',
        ],
    },
    test_suite='tests',
    license='GPLv3'
)
