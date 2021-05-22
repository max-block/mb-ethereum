import codecs
import os
import re

import setuptools
from pkg_resources import parse_requirements


def find_version(*file_paths):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *file_paths), "r") as fp:
        version_file = fp.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def load_requirements(f_name: str) -> list:
    requirements = []
    with open(f_name, "r") as fp:
        for req in parse_requirements(fp.read()):
            extras = "[{}]".format(",".join(req.extras)) if req.extras else ""
            requirements.append("{}{}{}".format(req.name, extras, req.specifier))  # type:ignore
    return requirements


setuptools.setup(
    name="mb-ethereum",
    version=find_version("mb_ethereum/__init__.py"),
    python_requires=">=3.9",
    packages=["mb_ethereum"],
    install_requires=[
        "click==8.0.1",
        "click-aliases==1.0.1",
        "halo==0.0.31",
        "PyYAML==5.4.1",
        "pydantic==1.8.2",
        "Jinja2==3.0.1",
        "eth-account==0.5.4",
        "websocket-client==1.0.1",
        "web3==5.19.0",
        "toml==0.10.2",
        "beautifulsoup4==4.9.3",
        "rlp==2.0.1",
        "cachetools==4.2.2",
        "mb-commons==0.1.0",
    ],
    extras_require={
        "dev": [
            "pytest==6.2.4",
            "pytest-xdist==2.2.1",
            "pre-commit==2.13.0",
            "PySnooper==0.5.0",
            "wheel==0.36.2",
            "twine==3.4.1",
            "python-dotenv==0.17.1",
        ],
    },
    entry_points={"console_scripts": ["mb-ethereum = mb_ethereum.cli:cli"]},
    include_package_data=True,
)
