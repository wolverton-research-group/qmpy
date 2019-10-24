import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'qmpy', 'VERSION.txt')) as fr:
    version = fr.read().strip()

setup(
    name='qmpy',
    version=version,
    author='The OQMD Development Team',
    author_email='oqmd.questions@gmail.com',
    license='LICENSE.txt',
    classifiers=["Programming Language :: Python :: 2.7"],
    packages=find_packages(),
    scripts=['bin/oqmd', 'bin/qmpy'],
    url='http://pypi.python.org/pypi/qmpy',
    description='Suite of computational materials science tools',
    include_package_data=True,
    long_description=open('README.md').read(),
    install_requires=[
        "Django == 1.8.18",
        "PuLP",
        "numpy < 1.17",
        "scipy < 1.3",
        "MySQL-python",
        "matplotlib < 3.0",
        "networkx < 2.3",
        "pytest < 5.0",
        "python-memcached",
        "ase < 3.18",
        "django-extensions < 1.6.8",
        "lxml",
        "spglib > 1.10",
        "PyCifRW >= 4.3",
        "pexpect",
        "pyparsing",
        "PyYAML",
        "scikit-learn < 0.21",
        "bokeh == 0.12.15",
        "djangorestframework == 3.6.4",
        "djangorestframework-xml",
        "djangorestframework-yaml",
        "djangorestframework-queryfields == 1.0.0",
        "djangorestframework-filters == 0.11.1",
        "django-crispy-forms",
        "lark-parser",
        "requests",
        "pygraphviz"
    ],
)
