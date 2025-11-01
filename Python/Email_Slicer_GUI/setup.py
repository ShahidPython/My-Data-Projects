from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="email-slicer",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Advanced Email Parsing and Analysis Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "questionary>=1.10.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "email-validator>=1.3.0",
        "tldextract>=3.4.0",
    ],
    entry_points={
        "console_scripts": [
            "email-slicer=main:main",
        ],
    },
)