from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.rst")) as handle:
    long_description = handle.read()

setup(
    name="pytest-cagoule",
    version="0.4.0",
    description="Pytest plugin to only run tests affected by changes",
    long_description=long_description,
    url="https://github.com/davidszotten/pytest-cagoule",
    author="David Szotten",
    author_email="davidszotten@gmail.com",
    packages=["pytest_cagoule"],
    install_requires=["coverage>=5", "pytest"],
    entry_points={
        "console_scripts": ["cagoule = pytest_cagoule.cmdline:main"],
        "pytest11": ["cagoule = pytest_cagoule.plugin"],
    },
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
)
