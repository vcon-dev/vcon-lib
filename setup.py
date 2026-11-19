from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="vcon",
    version="1.0.4",
    author="Thomas McCarthy-Howe",
    author_email="ghostofbasho@gmail.com",
    description="The vCon library - vCon 0.5.0 (draft-ietf-vcon-vcon-core-05) specification implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vcon-dev/vcon-lib",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
