from setuptools import setup

setup(
    name="pytest-cagoule",
    packages = ['pytest_cagoule'],

    entry_points = {
       'console_scripts': [
          'cagoule = pytest_cagoule.cmdline:main',
        ],
        'pytest11': [
            'cagoule = pytest_cagoule.plugin',
        ]
    },
)
