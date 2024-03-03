from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="postalservice",
    version="0.1.0",
    author="Aapo Montin",
    description="A package for second hand shopping",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Specify the content type
    packages=find_packages(),
)
