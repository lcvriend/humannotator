from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='humannotator',
    version='0.0.1',
    description='Library for building custom annotation tools',
    long_description=open('README.md').read(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.7',
        'Topic :: Text Processing :: Linguistic',
    ],
    keywords='annotation',
    url='http://github.com/lcvriend/humannotator',
    author='L.C. Vriend, D.E. Kim',
    author_email='vanboefer@gmail.com',
    license='GPLv3+',
    packages=['humannotator'],
    install_requires=[
        'pandas',
        'markdown',
    ],
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.6',
)
