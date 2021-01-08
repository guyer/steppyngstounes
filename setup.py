import setuptools

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="steppyngstounes",
    install_requires=["numpy", "future"],
    version="0.1",
    author="Jonathan E. Guyer",
    author_email="guyer@nist.gov",
    description="A package that provides iterators for advancing from start to stop",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/guyer/steppyngstounes",
    license="NIST Public Domain",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Science/Research",
        "License :: Public Domain",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7, <4'
)