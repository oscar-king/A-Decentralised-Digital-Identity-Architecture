import setuptools

setuptools.setup(
    name="crypto_utils",
    version="1.0.0",
    author="Oscar King",
    author_email="zcaboki@ucl.ac.uk",
    description="Blind Signature implementation and conversion functions.",
    url="https://github.com/oscar-king/A-Decentralised-Digital-Identity-Architecture/tree/master",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
