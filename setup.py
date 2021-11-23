import codecs

from os import path
from setuptools import find_packages, setup

from django_slowtests import __version__


def read(*parts):
    filename = path.join(path.dirname(__file__), *parts)
    with codecs.open(filename, encoding="utf-8") as fp:
        return fp.read()


setup(
    author="Michael Herman",
    author_email="michael@realpython.com",
    description="locate your slowest tests",
    name="django-slowtests",
    long_description=read("README.rst"),
    version=__version__,
    url="https://github.com/realpython/django-slow-tests",
    license="MIT",
    packages=find_packages(),
    tests_require=["Django>=1.6", "mock"],
    install_requires=["django>=1.6"],
    test_suite="runtests.runtests",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False
)
