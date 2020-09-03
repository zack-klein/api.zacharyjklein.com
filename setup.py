import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="northface",
    version="0.0.1",
    author="Zack Klein",
    author_email="klein.zachary.j@gmail.com",
    description=("Backend for http://zacharyjklein.com"),
    license="MIT",
    packages=["northface"],
    long_description=read("README.md"),
    entry_points={"console_scripts": ["zk = northface.handlers:cli_handler"]},
)
