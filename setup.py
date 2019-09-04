import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Decentralised DigID",
    version="0.0.1",
    author="Oscar King",
    author_email="zcaboki@ucl.ac.uk",
    description="Proof of Concept",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oscar-king/A-Decentralised-Digital-Identity-Architecture/tree/master",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)