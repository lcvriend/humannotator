from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='humannotator',
    version='0.0.1',
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
        'pandas',
        'markdown',
    ],
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.6',
)
