from qmpy import *

# We take the structure for (CH3NH3)PbI3 that is missing the H sites
struct = io.read('CNPbI3.cif')
n_h_bond = 1.01 #A
c_h_bond = 1.09 #A

def coord(vec):
    return struct.inv.T.dot(vec)

# and loop over atoms, adding H atoms to C and N atoms
for atom in struct:
    if atom.element.symbol == 'C':
        x = np.sin(np.pi/4)*c_h_bond
        x2 = np.sin(np.pi/4)*x
        ref = atom.cart_coord
        struct.add_atom(Atom.create('H', coord(ref+[x,   0.0, x])))
        struct.add_atom(Atom.create('H', coord(ref+[-x2, -x2, x])))
        struct.add_atom(Atom.create('H', coord(ref+[-x2,  x2, x])))
    elif atom.element.symbol == 'N':
        x = np.sin(np.pi/4)*n_h_bond
        x2 = np.sin(np.pi/4)*x
        ref = atom.cart_coord
        # Note the angles of the N's attached hydrogensare rotated
        # relative to the C's attached hydrogens.
        struct.add_atom(Atom.create('H', coord(ref+[-x, 0.0, -x])))
        struct.add_atom(Atom.create('H', coord(ref+[x2,  x2, -x])))
        struct.add_atom(Atom.create('H', coord(ref+[x2, -x2, -x])))

struct.symmetrize()
struct.save()
print struct.id
io.poscar.write(struct, 'POSCAR')
