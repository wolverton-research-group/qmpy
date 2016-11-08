from django.db import models
import logging

import qmpy
import qmpy.materials.element as elt

logger = logging.getLogger(__name__)

class Potential(models.Model):
    """
    Class for storing a VASP potential.

    Relationships:
        | calculation
        | element

    Attributes:
        | name
        | date
        | electrons: Electrons in potential.
        | enmax
        | enmin
        | gw
        | id
        | paw
        | potcar
        | us
        | xc


    """

    potcar = models.TextField()
    element = models.ForeignKey(elt.Element)

    name = models.CharField(max_length=10)
    xc = models.CharField(max_length=3)
    gw = models.BooleanField(default=False)
    paw = models.BooleanField(default=False)
    us = models.BooleanField(default=False)
    enmax = models.FloatField()
    enmin = models.FloatField()
    date = models.CharField(max_length=20)
    electrons = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'qmpy'
        db_table = 'vasp_potentials'

    def __str__(self):
        ident = '%s %s' % (self.name, self.xc)
        if self.paw:
            ident += ' PAW'
        if self.us:
            ident += ' US'
        if self.gw:
            ident += ' GW'
        return ident

    @classmethod
    def read_potcar(cls, potfile):
        '''
        Import pseudopotential(s) from VASP POTCAR. 

        Make sure to save each of them after importing
        in order to store in them in the OQMD

        Arguments:
            potfile - string, Path to POTCAR file

        Output:
            List of Potential objects
        '''

        # Read entire POTCAR file
        pots = open(potfile).read()

        # Split into the component POTCARs
        pots = pots.strip().split('End of Dataset')

        # Parse each file
        potobjs = []
        for pot in pots:
            if not pot:
                continue

            # Get key information from POTCAR
            potcar = {}
            for line in pot.split('\n'):

                # Get element name
                if 'TITEL' in line:
                    potcar['name'] = line.split()[3]
                    telt = potcar['name'].split('_')[0]
                    date = potcar['name'].split('_')[-1]
                    try:
                        potcar['element'] = elt.Element.objects.get(symbol=telt)
                    except:
                        print "Unknown element in potcar", telt
                        raise
                    if 'GW' in line:
                        potcar['gw'] = True
                    if 'PAW' in line:
                        potcar['paw'] = True
                    if 'US' in line:
                        potcar['us'] = True

                if 'ENMAX' in line:
                    data = line.split()
                    potcar['enmax'] = float(data[2].rstrip(';'))
                    potcar['enmin'] = float(data[5])

                if 'VRHFIN' in line:
                    potcar['electrons'] = line.split(':')[1]

                if 'LEXCH' in line:
                    key = line.split()[-1]
                    if key == '91':
                        potcar['xc'] = 'GGA'
                    elif key == 'CA':
                        potcar['xc'] = 'LDA'
                    elif key == 'PE':
                        potcar['xc'] = 'PBE'
            potobj, created = cls.objects.get_or_create(**potcar)
            if created:
                potobj.potcar = pot
            potobjs.append(potobj)
        return potobjs

class Hubbard(models.Model):
    """
    Base class for a hubbard correction parameterization.

    Attributes:
        | calculation
        | convention
        | correction
        | element
        | id
        | l
        | ligand
        | ox
        | u

    """
    element = models.ForeignKey(elt.Element, related_name='hubbards')
    convention = models.CharField(max_length=20)
    ox = models.FloatField(default=None, null=True)
    ligand = models.ForeignKey(elt.Element, related_name='+',
            null=True, blank=True)

    u = models.FloatField(default=0)
    l = models.IntegerField(default=-1)

    class Meta:
        app_label = 'qmpy'
        db_table = 'hubbards'

    def __nonzero__(self):
        if self.u > 0 and self.l != -1:
            return True
        else:
            return False

    def __eq__(self, other):
        if self.element != other.element:
            return False
        elif self.ligand != other.ligand:
            return False
        elif self.u != other.u:
            return False
        elif self.l != other.l:
            return False
        return True

    def __str__(self):
        retval = self.element_id
        if self.ox:
            retval += '+%d' % (self.ox)
        if self.ligand:
            retval += '-'+self.ligand_id
        retval += ', U=%0.2f, L=%d' % (self.u, self.l)
        return retval

    @property
    def key(self):
        return '%s_%s' % (self.element_id, self.u)

    @classmethod
    def get(cls, elt, ox=None, u=0, l=-1, lig=None):
        hub, new = Hubbard.objects.get_or_create(
                element_id=elt,
                ligand=lig, ox=ox,
                l=l, u=u)
        if new:
            hub.save()
        return hub
