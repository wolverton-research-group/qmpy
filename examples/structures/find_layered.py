from qmpy import *

structures = Structure.objects.filter(label='input', 
                                      entry__meta_data__value='icsd',
                                      entry__duplicate_of=None,
                                      natoms__lt=60)
f = open('layered.txt', 'w')
f.close()

for structure in structures:
    result = '3D'
    for i in range(3):
        sc = [ 1,1,1 ]
        sc[i] += 1
        lattice = structure.get_lattice_network(supercell=sc, tol=0.4)
        if not nx.is_connected(lattice.graph):
            result = 'LAYERED'
            break
    result += ' %s %s' % (structure.id, structure)
    print result
    open('layered.txt', 'a').write(result+'\n')

