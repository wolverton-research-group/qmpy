from setuptools import setup, find_packages

setup(
    name='qmpy',
    version='0.4.8',
    author='S. Kirklin',
    author_email='scott.kirklin@gmail.com',
    packages=find_packages(),
    scripts=['bin/oqmd', 'bin/qmpy'],
    url='http://pypi.python.org/pypi/qmpy',
    license='LICENSE.txt',
    description='Suite of computational materials science tools',
    long_description=open('README.txt').read(),
    package_data = {'': ['*.yml', '*.txt', 'legacy.dat', '*.cfg', '*.rst']},
    dependency_links = [
        'https://bitbucket.org/jamesrhester/pycifrw/downloads/PyCifRW-3.6.1.tar.gz#egg=PyCifRW==3.6.1'],
    install_requires=[
        "Django >= 1.5",
        "PuLP",
        "numpy >= 1.6.4",
        "scipy >= 0.12.0",
        "PyYAML",
        "MySQL-python",
        "matplotlib",
        "networkx",
        "pytest",
        "python-memcached",
        "python-ase",
        "django-extensions",
        "argparse"
    ],
)
