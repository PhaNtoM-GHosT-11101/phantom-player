from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="phantom-player",
    version="1.0.0",
    author="Aditya Priyadarshi",
    author_email="aditya@example.com",
    description="A cyberpunk-inspired, terminal-based YouTube Music engine.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PhaNtoM-GHosT-11101/phantom-player",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires='>=3.12',
    install_requires=[
        "textual>=0.40.0",
        "ytmusicapi>=1.0.0",
        "python-mpv-jsonipc>=1.2.0",
        "psutil>=5.9.0"
    ],
    entry_points={
        "console_scripts": [
            "adimusic=phantom_player.__main__:main",
            "phantom=phantom_player.__main__:main",
            "phantom-player=phantom_player.__main__:main"
        ],
    },
)
