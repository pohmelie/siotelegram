import os
import re
import pathlib

from setuptools import setup, find_packages


def read(f):
    return (pathlib.Path(__file__).parent / f).read_text("utf-8").strip()


try:
    version = re.findall(r"""^__version__ = "([^']+)"\r?$""",
                         read(os.path.join("siotelegram", "__init__.py")),
                         re.M)[0]
except IndexError:
    raise RuntimeError("Unable to determine version.")


setup(
    name="siotelegram",
    version=version,
    description=("Sans io telegram api with couple io backends"),
    long_description=read("readme.md"),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    author="pohmelie",
    author_email="multisosnooley@gmail.com",
    url="https://github.com/pohmelie/siotelegram",
    license="WTFPL",
    packages=find_packages(),
    python_requires=">= 3.7",
    install_requires=[],
    extras_require={
        "aiohttp": [
            "aiohttp",
            "async_timeout >= 1.2.0",
        ],
        "httpx": [
            "httpx",
            "async_timeout",
        ],
        "requests": [
            "requests",
        ]
    },
    include_package_data=True,
)
