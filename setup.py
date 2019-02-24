import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="UH-OPCunix-JGirdwood",
    version="0.1.1",
    author="Joseph Girdwood",
    author_email="j.girdwood@herts.ac.uk",
    description="A package to interface a UCASS with a linux computer via USB-ISS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JGirdwood/OPCunix",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
    install_requires=[
        'pyserial',
        'pyusbiss'
    ],
)
