import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fintoolbox",
    version="0.0.2",
    author="Aurélien Roy",
    author_email="aurelien.roy@outlook.com",
    description="Basic functions to process financial time series with pandas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
)