from setuptools import setup, find_packages

setup(
    name='qmpy',
    version='0.4.9a',
    author='S. Kirklin',
    author_email='scott.kirklin@gmail.com',
    license='LICENSE.txt',
    classifiers=["Programming Language :: Python :: 2.7"],
    packages=find_packages(),
    scripts=['bin/oqmd', 'bin/qmpy'],
    url='http://pypi.python.org/pypi/qmpy',
    description='Suite of computational materials science tools',
    include_package_data=True,
    long_description=open('README.md').read(),
    install_requires=[
        "Django >=1.6.2, <1.7",
        "PuLP",
        "numpy",
        "scipy",
        "MySQL-python",
        "matplotlib",
        "networkx",
        "pytest",
        "python-memcached",
        "ase",
        "django-extensions < 1.6.8",
        "lxml",
        "pyspglib == 1.8.3.1",
        "PyCifRW >= 4.3",
        "pexpect",
        "pyparsing",
        "PyYAML",
        "scikit-learn"
        "bokeh == 0.12.11"
    ],
)
