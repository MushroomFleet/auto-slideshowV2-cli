#!/usr/bin/env python3
"""
Setup script for Auto-Slideshow Generator V2
"""

from setuptools import setup, find_packages
import os

# Read the version from v2/__init__.py
with open(os.path.join('v2', '__init__.py'), 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"\'')
            break
    else:
        version = '0.0.0'

# Read README for long description
try:
    with open('README.md', 'r') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "A tool for creating beautiful slideshows from your image collections."

setup(
    name="auto-slideshow",
    version=version,
    author="Auto-Slideshow Team",
    author_email="example@example.com",
    description="A tool for creating beautiful slideshows from your image collections",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/auto-slideshow",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'opencv-python>=4.5.0',
        'numpy>=1.19.0',
        'Pillow>=8.0.0',
        'librosa>=0.8.0',
        'soundfile>=0.10.0',
    ],
    entry_points={
        'console_scripts': [
            'autoslideshow=v2.main:main',
        ],
    },
)
