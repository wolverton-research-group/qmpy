wget http://downloads.sourceforge.net/project/spglib/spglib/spglib-1.6/spglib-1.6.0.tar.gz
tar -xvf spglib-1.6.0.tar.gz
cd spglib-1.6.0
./configure
make
cd python/ase
python setup.py install
