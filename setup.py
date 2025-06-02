"""Setup configuration for SearchFlox PyPI package"""

from setuptools import setup, find_packages
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="searchflox",
    version="1.0.2",
    author="KOBULA & UTKRASH RISHI",
    author_email="arcdev.90@gmail.com",
    description="AI-Powered Research Platform - Advanced CLI tool for intelligent research and report generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ArcDevs/searchflox",
    project_urls={
        "Bug Reports": "https://github.com/ArcDevs/searchflox/issues",
        "Source": "https://github.com/ArcDevs/searchflox",
        "Documentation": "https://github.com/ArcDevs/searchflox#readme",
    },
    packages=find_packages(), 
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Text Processing :: General",
        "Topic :: Utilities",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.910",
            "pre-commit>=2.15.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "sphinx-autodoc-typehints>=1.12",
        ],
    },
    entry_points={
        "console_scripts": [
            "searchflox=searchflox.main:main",  
            "sf=searchflox.main:main",       
        ],
    },
    keywords=[
        "ai", "research", "search", "cli", "artificial-intelligence",
        "websocket", "automation", "report-generation", "data-analysis",
        "intelligence", "academic", "professional", "async", "real-time",
        "searchflox"
    ],
    package_data={
        "searchflox": [
            "config/*.json",
            "templates/*.txt",
            "assets/*",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    platforms=["any"],
    license="MIT",
    license_files=["LICENSE"],
)