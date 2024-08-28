from setuptools import setup, find_packages


with open("Readme.md", "r") as f:
    long_description = f.read()


setup(
    name="nullsweep",
    version="0.1.0",
    description="A comprehensive Python package for managing and analyzing missing data in pandas DataFrames, starting with detection and expanding to complete handling.",
    package_dir={"": "nullsweep"},
    packages=find_packages(where="nullsweep"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/okanyenigun/nullsweep",
    author="Okan Yenigün",
    author_email="okanyenigun@gmail.com",
    license="MIT",
    classifiers=[
    'Development Status :: 3 - Alpha',  
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Scientific/Engineering :: Mathematics',
    'License :: OSI Approved :: MIT License', 
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Operating System :: OS Independent'
    ],
    install_requires=[
        'pandas==2.2.2',
        'scipy==1.13.1',
        'statsmodels==0.14.2',
        'scikit-learn==1.5.1',
        ],
    extras_require={
        'dev': ['twine==5.1.1'],
        'test': ['pytest==8.2.2']
    },
    python_requires='>=3.7',
)