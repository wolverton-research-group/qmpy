from setuptools import setup, find_packages

setup(
    name='qmpy',
<<<<<<< HEAD
    version='2.0.0a',
    author='S. Kirklin <scott.kirklin@gmail.com>',
    author_email='oqmd.questions@gmail.com',
    license='LICENSE.txt',
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7"
    ],
=======
    version='0.4.9a',
    author='S. Kirklin',
    author_email='scott.kirklin@gmail.com',
    license='LICENSE.txt',
    classifiers=["Programming Language :: Python :: 2.7"],
>>>>>>> ca8b049cf0a069dfad285aae4258ffaac3deea64
    packages=find_packages(),
    scripts=['bin/oqmd', 'bin/qmpy'],
    url='http://pypi.python.org/pypi/qmpy',
    description='Suite of computational materials science tools',
    include_package_data=True,
    long_description=open('README.md').read(),
    install_requires=[
<<<<<<< HEAD
        "Django == 1.6.2",
        "PuLP",
        "numpy == 1.8.1",
        "scipy >= 0.12.0",
        "MySQL-python == 1.2.5",
=======
        "Django >=1.6.2, <1.7",
        "PuLP",
        "numpy",
        "scipy",
        "MySQL-python",
>>>>>>> ca8b049cf0a069dfad285aae4258ffaac3deea64
        "matplotlib",
        "networkx",
        "pytest",
        "python-memcached",
        "ase",
        "django-extensions",
        "lxml",
<<<<<<< HEAD
        "pyparsing <= 1.9.9",
        "PyCifRW >= 3.6.2.1",
=======
        "pyspglib",
        "PyCifRW",
>>>>>>> ca8b049cf0a069dfad285aae4258ffaac3deea64
        "pexpect",
        "pyparsing",
        "PyYAML",
        "scikit-learn"
    ],
)
