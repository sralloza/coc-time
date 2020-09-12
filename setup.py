from pathlib import Path

from setuptools import find_packages, setup

import versioneer

requirements = Path(__file__).with_name("requirements.txt").read_text().splitlines()

setup(
    name="coc",
    version=versioneer.get_version(),
    author="Diego Alloza",
    entry_points={"console_scripts": ["coc=coc_time:cli"]},
    include_package_data=True,
    author_email="coc-time-support@sralloza.es",
    url="git+http://github.com/sralloza/coc-time.git",
    install_requires=requirements,
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
)
