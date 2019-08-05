from setuptools import setup

setup(
    name='humannotator',
    version='0.1',
    description='Library for manual annotation',
    long_description='Library for building custom manual annotation tools.',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python :: 3.7',
        'Topic :: Text Processing :: Linguistic',
        ],
    keywords='annotation',
    url='http://github.com/lcvriend/humannotator',
    author='L.C. Vriend, D.E. Kim',
    author_email='vanboefer@gmail.com',
    license='LGPLv3+',
    packages=['humannotator'],
    install_requires=[
        'pandas',
        ],
    include_package_data=True,
    zip_safe=False,
    )
