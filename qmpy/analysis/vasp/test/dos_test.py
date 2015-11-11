from qmpy import DOS, io

strc = io.read('../files/relaxation/POSCAR')
dos = DOS.read('../files/relaxation/DOSCAR')

# Get the total DOS
print "Getting total DOS..."
total_dos = dos.dos
#print total_dos
my_dos = dos.get_projected_dos(strc, 'Mg', debug=True)
my_dos = my_dos / 2
#print my_dos
error = max([ abs(x) for x in (total_dos - my_dos)])
print error

# Get only d orbitals
print "Getting d orbital DOS..."
dos.get_projected_dos(strc, 'Mg', orbital='d', debug=True)
