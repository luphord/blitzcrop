#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""blitzcrop setup script.
"""

from setuptools import setup

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("HISTORY.md") as history_file:
    history = history_file.read()

requirements = ["Pillow==9.1.0"]

test_requirements = []

setup(
    author="luphord",
    author_email="luphord@protonmail.com",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    description="""GUI for interactive batch image cropping.""",
    entry_points={
        "console_scripts": [
            "blitzcrop=blitzcrop:main",
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    include_package_data=True,
    data_files=[(".", ["LICENSE", "HISTORY.md"])],
    keywords="blitzcrop",
    name="blitzcrop",
    py_modules=["blitzcrop"],
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/luphord/blitzcrop",
    version="0.1.0",
    zip_safe=True,
)
