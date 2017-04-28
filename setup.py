from setuptools import setup, find_packages

setup(
    name='qmpy',
    version='1.1.0',
    author='S. Kirklin',
    author_email='scott.kirklin@gmail.com',
    license='LICENSE.txt',
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7"
    ],
    packages=find_packages(),
    scripts=['bin/oqmd', 'bin/qmpy'],
    url='http://pypi.python.org/pypi/qmpy',
    description='Suite of computational materials science tools',
    include_package_data=True,
    long_description=open('README.md').read(),
    install_requires=[
        "Django == 1.6.2",
        "PuLP",
        "numpy == 1.8.1",
        "scipy >= 0.12.0",
        "MySQL-python == 1.2.5",
        "matplotlib",
        "networkx",
        "pytest",
        "python-memcached",
        "ase",
        "django-extensions",
        "lxml",
        "pyspglib",
        "PyCifRW == 3.6.2.1",
        "pexpect",
        "PyYAML",
        "scikit-learn"
    ],
)
