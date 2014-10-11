from setuptools import setup

setup(
    name="cagoule",
    packages = ['cagoule'],

    entry_points = {
       'console_scripts': [
          'cagoule = cagoule.cmdline:main',
        ],
        'pytest11': [
            'cagoule = cagoule.plugin',
        ]
    },
)
