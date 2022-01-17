import os
from setuptools import setup, find_packages
from distutils.sysconfig import get_python_inc
import pathlib

# python include dir
py_include_dir = os.path.join(get_python_inc())

__version__ = "1.0"

setup(
    name="bbsQt",
    version=__version__,
    author="DeepInsight",
    packages=find_packages(),
    author_email="hschoi@dinsight.ai",
    url="https://github.com/Hoseung/Kinect_BBS_demo",
    description="BBS scoring application using fully homomorphic encryption over TCP socket communication",
    long_description="",
    zip_safe=False,
)