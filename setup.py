from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="postalservice",
    version="0.2.0",
    author="Aapo Montin",
    description="A package for second hand shopping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "cryptography",
        "httpx",
        "jose",
        "python_jose",
        "setuptools",
        "bs4",
        "lxml",
        "playwright",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest_mock",
            "pytest-asyncio",
        ],
    },
    python_requires=">=3.7",
)
