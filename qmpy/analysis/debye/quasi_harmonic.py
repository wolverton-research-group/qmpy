## Mostly from Physical Acoustics V.IIIB - W.P. Mason ed. 1965 [534 M412p] Ch. 1-2 
## Also in Journal of Alloys and Compounds 353 (2003) 74–85
## Data here for Co3O4

# need to determine units for these values
mass = 240.79500/7/1000./6.0221415e23 # average atomic mass in ?kg/atom?
N = 1. #number of atoms per unit cell (related to density…)
V = 9.51215e-30 # volume in ?m^3?
density = mass/V # mass density in ?kg/m^3?

kb=1.3806504e-23 # Boltzmann's constant, J/atom-K
hbar=1.05457148e-34 # Planck's constant by 2pi, J-s
#elastic tensor (in kbar from VASP)
elast=zeros((6,6))
elast[0,0]=2864.3795
elast[1,1]=elast[0,0]
elast[2,2]=elast[0,0]
elast[0,1]=1465.6047
elast[0,2]=elast[0,1]
elast[1,0]=elast[0,1]
elast[1,2]=elast[0,1]
elast[2,0]=elast[0,1]
elast[2,1]=elast[0,1]
elast[3,3]=863.7687
elast[4,4]=elast[3,3]
elast[5,5]=elast[3,3]
elast=elast/10 # convert to GPa
compl=inv(elast) # compliance tensor

#Voigt bulk, shear, Young's moduli
B_v=1/9.*(elast[0,0]+elast[1,1]+elast[2,2]+2*(elast[0,1]+elast[1,2]+elast[2,0]))
G_v=1/15.*(elast[0,0]+elast[1,1]+elast[2,2]-(elast[0,1]+elast[1,2]+elast[2,0])+3*(elast[3,3]+elast[4,4]+elast[5,5]))
Y_v=9.*(B_v*G_v)/(3.*B_v+G_v)

#Reuss bulk, shear, Young's moduli
B_r=1/(compl[0,0]+compl[1,1]+compl[2,2]+2.*(compl[0,1]+compl[1,2]+compl[2,0]))
G_r=15.*1/(4.*(compl[0,0]+compl[1,1]+compl[2,2])-4.*(compl[0,1]+compl[1,2]+compl[2,0])+3.*(compl[3,3]+compl[4,4]+compl[5,5]))
Y_r=9.*(B_r*G_r)/(3.*B_r+G_r)

#Hill's VRH averages
B_vrh=0.5*(B_v+B_r)
G_vrh=0.5*(G_v+G_r)
Y_vrh=0.5*(Y_v+Y_r)

#Longitudinal modulus
M_vrh=0.5*(B_vrh+4*G_vrh)


#### Debye temp from isotropic approximation
vel_s=sqrt(G_vrh*1e9/density) # shear (transverse) sound velocity
vel_l=sqrt((B_vrh*1e9+4/3.*G_vrh*1e9)/density) # longitudinal sound velocity (4/3 or 4/2?)
vel_avg=(1/3.*(1/vel_l**3+2./vel_s**3))**(-1/3.) # average sound velocity
Td=hbar*vel_avg/kb*(6.*pi**2.*N/V)**(1/3.)	



### Debye temp directly from elastic constants
# sound_vel constructs the characteristic (secular) equation, from which the primary sound velocities are derived
def sound_vel(theta,phi):
    #convert spherical coords to cartesian with r=1, then calculate direction cosines
    x=sin(theta)*cos(phi)
    y=sin(theta)*sin(phi)
    z=cos(theta)
    wave=array([x,y,z]) # wave propagation vector
    #direction cosines
    l=wave[0]/sqrt(wave[0]**2.+wave[1]**2.+wave[2]**2.)
    m=wave[1]/sqrt(wave[0]**2.+wave[1]**2.+wave[2]**2.)
    n=wave[2]/sqrt(wave[0]**2.+wave[1]**2.+wave[2]**2.)
    G11=l**2.*elast[0,0]+m**2.*elast[5,5]+n**2.*elast[4,4]+2*m*n*elast[4,5]+2*n*l*elast[0,4]+2*l*m*elast[0,5]
    G22=l**2.*elast[5,5]+m**2.*elast[1,1]+n**2.*elast[3,3]+2*m*n*elast[1,3]+2*n*l*elast[3,5]+2*l*m*elast[1,5]
    G33=l**2.*elast[4,4]+m**2.*elast[3,3]+n**2.*elast[2,2]+2*m*n*elast[2,3]+2*n*l*elast[2,4]+2*l*m*elast[3,4]
    G12=l**2.*elast[0,5]+m**2.*elast[1,5]+n**2.*elast[3,4]+m*n*(elast[3,5]+elast[1,4])+n*l*(elast[0,3]+elast[4,5])+l*m*(elast[0,1]+elast[5,5])
    G13=l**2.*elast[0,4]+m**2.*elast[3,5]+n**2.*elast[2,4]+m*n*(elast[3,4]+elast[2,5])+n*l*(elast[0,2]+elast[4,4])+l*m*(elast[0,3]+elast[4,5])
    G23=l**2.*elast[4,5]+m**2.*elast[1,3]+n**2.*elast[2,3]+m*n*(elast[3,3]+elast[1,2])+n*l*(elast[2,5]+elast[3,4])+l*m*(elast[1,4]+elast[3,5])
    sec=array([[G11,G12,G13],[G12,G22,G23],[G13,G23,G33]])
    return sqrt(eig(sec)[0]*1e9/density) #the eigenvalues are density*sound velocity^2

from scipy import integrate
int_sv=integrate.dblquad(lambda t, p: (sound_vel(t,p)[0]**-3.+sound_vel(t,p)[1]**-3.+sound_vel(t,p)[2]**-3.), 0.,pi, lambda p: 0., lambda p: 2.*pi)[0]
avg_sv=(int_sv/(4.*pi))**(-1/3.)
Td=(hbar*2.*pi)/kb*(9./(4.*pi)*N/V)**(1/3.)*avg_sv

def point_sv(t,x):
    return (sound_vel(t,x)[0]**-3.+sound_vel(t,x)[1]**-3.+sound_vel(t,x)[2]**-3.)




