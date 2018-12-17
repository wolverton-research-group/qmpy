from setuptools import setup, find_packages

with open('README.md', 'r') as fr:
    long_description = fr.read()

setup(
    name='qmpy',
    version='2.0.0a',
    author='S. Kirklin',
    author_email='scott.kirklin@gmail.com',
    license='LICENSE.txt',
    classifiers=["Programming Language :: Python :: 2.7"],
    packages=find_packages(),
    scripts=['bin/oqmd', 'bin/qmpy'],
    url='http://pypi.python.org/pypi/qmpy',
    description='Suite of computational materials science tools',
    include_package_data=True,
    long_description=long_description,
    install_requires=[
        "Django <= 2.0",
        "PuLP",
        "numpy",
        "scipy",
        "MySQL-python",
        "matplotlib",
        "networkx",
        "pytest",
        "python-memcached",
        "ase",
        "django-extensions",
        "lxml",
        "spglib",
        "PyCifRW >= 4.3",
        "pexpect",
        "PyYAML",
        "scikit-learn",
        "bokeh == 0.12.15"
    ],
)
