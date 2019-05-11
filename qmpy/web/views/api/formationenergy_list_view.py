from rest_framework import generics
import django_filters.rest_framework
from qmpy.web.serializers.formationenergy import FormationEnergySerializer
from qmpy.materials.formation_energy import FormationEnergy
from qmpy.materials.entry import Composition
from qmpy.utils import Token, parse_formula_regex

DEFAULT_LIMIT = 50

class FormationEnergyDetail(generics.RetrieveAPIView):
    queryset = FormationEnergy.objects.all()
    serializer_class = FormationEnergySerializer

class FormationEnergyList(generics.ListAPIView):
    serializer_class = FormationEnergySerializer

    def get_queryset(self):
        fes = FormationEnergy.objects.filter(fit="standard")
        fes = self.icsd_filter(fes)
        fes = self.composition_filter(fes)
        fes = self.filter(fes)

        sort_fes = self.request.GET.get('sort_by', False)

        if not sort_fes:
            return fes
        else:
            limit = self.request.GET.get('limit')
            sort_offset = self.request.GET.get('sort_offset')
            try:
                limit = int(limit)
            except:
                limit = DEFAULT_LIMIT
            try:
                sort_offset = int(sort_offset)
            except:
                sort_offset = 0
            desc = self.request.GET.get('desc', False)

        if sort_fes == 'stability':
            fes = self.sort_by_stability(fes, limit, sort_offset, desc)

        return fes

    def icsd_filter(self, fes):
        request = self.request
        ificsd = request.GET.get('icsd', None)
        
        if ificsd == None:
            return fes
        elif ificsd in ['False', 'false', 'F', 'f']:
            return fes.exclude(entry__path__contains='/icsd/')
        elif ificsd in ['True', 'true', 'T', 't']:
            return fes.filter(entry__path__contains='/icsd/')

        return fes

    def composition_filter(self, fes):
        """
        Valid url parameter inputs:
            1. ?composition=Fe2O3
            2. ?composition=Fe-O
            3. ?composition={Fe,Ni}O
            4. ?composition={3d}2O3
        """
        request = self.request

        comp = request.GET.get('composition', False)
        if not comp:
            return fes

        if '{' and '}' in comp:
            c_dict_lst = parse_formula_regex(comp)
            f_lst = []
            for cd in c_dict_lst:
                f = ' '.join(['%s%g' % (k, cd[k]) for k in sorted(cd.keys())])
                f_lst.append(f)
            fes = fes.filter(composition__formula__in=f_lst)
        else:
            c_lst = comp.strip().split('-')
            cs = Composition.get_list(c_lst)
            if len(cs) == 1:
                c = cs[0]
            else:
                c = cs
            fes = fes.filter(composition=c)

        return fes


    def filter(self, fes):
        """
        Valid attributes:
            element, generic, prototype, spacegroup,
            volume, natoms, ntypes, stability,
            delta_e, band_gap

        Requirments:
            1. Space padding is required between expression. 
            2. For each epression, space is not allowed.
            3. Operators include: 'AND', 'OR'
            4. '(' and ')' can be used to change precedence
            5. For numerical attributes, we can have '>' or '<' conditions.
            Valid examples:
                'element=Mn AND band_gap>1'
                '( element=O OR element=S ) AND natoms<3'
            Invalid examples:
                'element = Fe'
                '( element=Fe And element=O)'

        Additionally, instead of multiple 'element' expressions, we can use
        'element_set' expression to combine elements in the filter.

        Format of element_set expression:
            ',': AND operator
            '-': OR operator
            '(', ')': to change precedence
            Examples:
                element_set=Al;O,H
                element_set=(Mn;Fe),O
        """
        request = self.request

        filters = request.GET.get('filter', False)

        if not filters:
            return fes

        # replace 'AND', 'OR' and 'NOT' to '&' ,'|' and '~', respectively
        filters = filters.replace('AND', '&')
        filters = filters.replace('OR', '|')
        filters = filters.replace('NOT', '~')

        t = Token(filters)
        q = t.evaluate_filter(origin='formationenergy')
        fes = fes.filter(q)

        return fes

    def sort_by_stability(self, fes, limit=DEFAULT_LIMIT, sort_offset=0, desc=False):
        if desc in ['T', 't', 'True', 'true']:
            ordered_fes = fes.order_by('-stability')
        else:
            ordered_fes = fes.order_by('stability')
        return ordered_fes[sort_offset:sort_offset+limit]
