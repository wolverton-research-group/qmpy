import matplotlib
params = {'font.size': 16,
          'text.color':'k',
          'axes.labelcolor':'k',
          'xtick.color':'k',
          'ytick.color':'k',
          'font.family':'serif',
          'axes.edgecolor':'grey',
          'font.serif':['Century']}
matplotlib.rcParams.update(params)
import matplotlib.pylab as plt
import numpy as np
#import yaml
import pickle

def chunks(l, n):
    '''Return n roughly evenly sized chunks from l. The last will always be shortest'''
    N = int(np.ceil(float(len(l))/float(n)))
    for i in xrange(0, len(l), N):
        yield l[i:i+N]

if False:
    data = open('chemical_potentials.yml').read()
    chem_pots = yaml.load(data)
    
    data = open('data.yml').read()
    elements = yaml.load(data)
    open('data.pkl', 'w').write(pickle.dumps([chem_pots, elements]))
else:
    chem_pots, elements = pickle.loads(open('data.pkl').read())

nothing = chem_pots['nothing']['elements']
everything = chem_pots['everything']['elements']
standard = chem_pots['standard']['elements']

elts = np.array(sorted(nothing.keys(), key=lambda x: elements[x]['z']))

for elt in elts:
    if abs(everything[elt] - nothing[elt]) > 0.2:
        print elt, everything[elt], nothing[elt]
        
rows = 4
fig = plt.figure(frameon=False)
first = True

for i, telts in enumerate(chunks(elts, rows)):
    telts = elts[i*len(elts)/rows:(i+1)*len(elts)/rows]
    ind = np.arange(len(telts))
    print len(telts)

    width = 0.65
    
    ax = fig.add_subplot(1, rows, i+1)
    ax.barh(ind+width+(1-width),
           [ everything[elt] - nothing[elt] for elt in telts ],
           0.45,
           color='r',
           label='Fit-all')
    ax.barh(ind+width,
           [ standard[elt] - nothing[elt] for elt in telts ],
           0.45,
           color='b',
           label='Fit-partial')

    #ax.set_xticks(ind + width + width/2)
    #ax.set_xticklabels(telts)
    #ax.set_xticks([])
    #ax.axis('off')
    ax.yaxis.set_visible(False)
    plt.xlabel('Correction [eV/atom]')
    plt.xlim([-1, 1])
    plt.ylim([0, 27])
    

    for x, elt in enumerate(telts):
        ax.text(max(0, everything[elt] - nothing[elt], standard[elt] - nothing[elt])+0.1, x+1, 
                elt, va='center', ha='left')

    if first:
        plt.legend(loc='best')
        first = False


##plt.legend(bbox_to_anchor=(0., 0.), loc=2,
##       ncol=1, borderaxespad=0.)

#plt.tight_layout()
fig.set_size_inches(15.5,7.5)

#plt.show()
plt.savefig('chempots.eps', bbox_inches='tight')
