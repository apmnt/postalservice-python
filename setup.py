from setuptools import setup, find_packages

setup(
    name="postalservice",
    version="0.1.0",
    author="Aapo Montin",
    description="A package for second hand shopping",
    packages=find_packages(),
    long_description_content_type="text/markdown",
    long_description=open("README.md").read(),
)
