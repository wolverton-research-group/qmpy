from setuptools import setup, find_packages

setup(
    name='qmpy',
    version='1.1.0',
    author='S. Kirklin',
    author_email='scott.kirklin@gmail.com',
    packages=find_packages(),
    scripts=['bin/oqmd', 'bin/qmpy'],
    url='http://pypi.python.org/pypi/qmpy',
    license='LICENSE.txt',
    description='Suite of computational materials science tools',
    include_package_data=True,
    long_description=open('README.md').read(),
    install_requires=[
        "Django == 1.6.11",
        "PuLP",
        "numpy == 1.8.1",
        "scipy >= 0.12.0",
        "MySQL-python",
        "matplotlib",
        "networkx",
        "pytest",
        "python-memcached",
        "ase",
        "django-extensions",
        "lxml",
        "pyparsing<=1.9.9",
        "PyCifRW==3.6.2.1",
        "pexpect",
        "PyYAML",
        "scikit-learn"
    ],
)
