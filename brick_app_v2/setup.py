#!/usr/bin/env python3
"""
Setup script for SHACL Brick Generator package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="shacl-brick-app",
    version="1.0.0",
    author="SHACL System Developer",
    author_email="developer@example.com",
    description="SHACL Brick Generator - Step 1 of Three-Step SHACL System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/shacl-brick-app",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt6",
        "rdflib",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-qt",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "shacl-brick-gui=shacl_brick_app.bricks:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
