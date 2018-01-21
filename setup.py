from setuptools import setup


setup(
    name='eco_parser',
    author="chris48s",
    license="MIT",
    url="https://github.com/DemocracyClub/eco-parser/",
    packages=['eco_parser'],
    entry_points={
        'console_scripts': [
            'eco_parser = eco_parser.__main__:main'
        ]
    },
    install_requires=[
        'lxml',
        'requests',
    ],
)
