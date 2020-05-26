from setuptools import setup, find_packages
from pathlib import Path

# The project root directory
root_dir = Path(__file__).parent

# Description and README
description = 'RL environments for poker games'
readme = (root_dir / 'README.md').read_text()

# Versioning
MAJOR = 0
MINOR = 0
PATCH = 3
version = '{:d}.{:d}.{:d}'.format(MAJOR, MINOR, PATCH)
pyversion = '>=3.6'

# Repo and author
author = 'Andrea Mecchia, Guglielmo Manneschi',
author_email = 'mecchia.andrea@gmail.com'
github = 'https://github.com/sneppy/pokerl'
lic = 'MIT'

# PyPi classifiers
classifiers = [
	'Development Status :: 1 - Planning',
	'Operating System :: OS Independent',
	'Programming Language :: Python :: 3.6',
	'Programming Language :: Python :: 3.7',
	'Programming Language :: Python :: 3.8',
	'Programming Language :: Python :: 3.9',
	'Topic :: Scientific/Engineering :: Artificial Intelligence',
	'Intended Audience :: Science/Research',
	'License :: OSI Approved :: MIT License',
	'Natural Language :: English'
]

# Packages and dependencies
packages = find_packages()
dependencies = ['numpy >= 1.18.0']

setup(
	name='pokerl',
	description=description,
	long_description=readme,
	long_description_content_type='text/markdown',
	version=version,
	python_requires=pyversion,
	author=author,
	author_email=author_email,
	url=github,
	license=lic,
	classifiers=classifiers,
	packages=packages,
	install_requires=dependencies,
	zip_safe=False
)