from qmpy import DOS, io
from numpy import mean

strc = io.read('../files/relaxation/POSCAR')
dos = DOS.read('../files/relaxation/DOSCAR')

# Get the total DOS
print "Getting total DOS..."
total_dos = dos.dos
my_dos = dos.get_projected_dos(strc, 'Mg', debug=True)
my_dos = my_dos * 2 * (dos.energy[1] - dos.energy[0])
error = mean([ abs(x) for x in (total_dos - my_dos)])
print "\tMean difference between total DOS and projected: ", error

# Get only d orbitals
print "Getting d orbital DOS..."
dos.get_projected_dos(strc, 'Mg', orbital='d', debug=True)
