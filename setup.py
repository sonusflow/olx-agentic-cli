"""Setup script for olx-agentic-cli."""

from setuptools import setup, find_packages

setup(
    name="olx-agentic-cli",
    version="1.0.0",
    description="CLI tool for the OLX Partner API v2.0",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="sonusflow",
    author_email="claudflare@sonusflow.pl",
    url="https://github.com/sonusflow/olx-agentic-cli",
    license="MIT",
    packages=find_packages(),
    py_modules=["cli", "config"],
    python_requires=">=3.10",
    install_requires=[
        "httpx>=0.27,<1.0",
        "click>=8.1,<9.0",
    ],
    entry_points={
        "console_scripts": [
            "olx=cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
