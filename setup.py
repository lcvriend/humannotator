import re
from pathlib import Path
from setuptools import setup, find_packages

PATH = Path(__file__).resolve().parent

def get_version(filename):
    regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
    file = PATH / filename
    file_content = file.read_text(encoding='utf8')
    version_match = re.search(regex, file_content, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='humannotator',
    version=get_version('humannotator/version.py'),
    description='Customizable tool for easy manual annotation',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Utilities',
    ],
    keywords='annotation annotator text data pandas',
    url='http://github.com/lcvriend/humannotator',
    author='L.C. Vriend, D.E. Kim',
    author_email='vanboefer@gmail.com',
    license='GPLv3+',
    packages=find_packages(),
    install_requires=[
        'pandas>=0.24.0',
        'markdown',
    ],
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.6',
)
