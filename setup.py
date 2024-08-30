from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="vcon",
    version="0.3.3",
    author="Thomas McCarthy-Howe",
    author_email="ghostofbasho@gmail.com",
    description="A package for working with vCon containers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vcon-dev/vcon-lib",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)