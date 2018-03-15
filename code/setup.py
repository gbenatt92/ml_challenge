from setuptools import setup, find_packages

VERSION = "0.0.1"

DEPENDENCIES = [
    "numpy"
]

setup(
    name='ml-challenge',
    version=VERSION,
    description='Machine Learning Challenge',
    author='Gabriel Alvim',
    author_email='gabriel.b.alvim@gmail.com',
    packages=find_packages(),
    install_requires=DEPENDENCIES,  # external packages as dependencies
)
