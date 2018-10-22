from rest_framework import generics
import django_filters.rest_framework
from qmpy.web.serializers.entry import EntrySerializer
from qmpy.materials.entry import Entry, Composition
from qmpy.materials.formation_energy import FormationEnergy
from qmpy.analysis.vasp import Calculation
from api_perm import *
from qmpy.utils import Token, parse_formula_regex

class EntryDetail(generics.RetrieveAPIView):
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer

class EntryList(generics.ListAPIView):
    #permission_classes = (OnlyAPIPermission, )
    serializer_class = EntrySerializer
    #filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def get_queryset(self):
        entries = Entry.objects.all()
        entries = self.composition_filter(entries)
        entries = self.calculated_filter(entries)
        entries = self.bandgap_filter(entries)
        entries = self.ntypes_filter(entries)
        entries = self.generic_filter(entries)

        sort_entries = self.request.GET.get('sort_by', False)

        if not sort_entries:
            return entries
        else:
            sort_limit = self.request.GET.get('sort_limit')
            sort_offset = self.request.GET.get('sort_offset')
            try:
                sort_limit = int(sort_limit)
            except:
                sort_limit = 100
            try:
                sort_offset = int(sort_offset)
            except:
                sort_offset = 0
            desc = self.request.GET.get('desc', False)

        if sort_entries == 'bandgap':
            entries = self.sort_by_bandgap(entries, sort_limit, sort_offset, desc)
        elif sort_entries == 'formationenergy':
            entries = self.sort_by_formationenergy(entries, sort_limit, sort_offset, desc)
        elif sort_entries == 'energyperatom':
            entries = self.sort_by_energyperatom(entries, sort_limit, sort_offset, desc)

        return entries

    def composition_filter(self, entries):
        """
        Valid url parameter inputs:
            1. ?composition=Fe2O3
            2. ?composition=Fe-O
            3. ?composition={Fe,Ni}O
            4. ?composition={3d}2O3
            5. ?composition=include_(Fe,Mn)-O : (Fe OR Mn) AND O
            6. ?composition=include_Cl,O-H : Cl OR O AND H 
            6. ?composition=include_H-{3d} : 3d elements AND H
        """
        request = self.request

        comp = request.GET.get('composition', False)
        if not comp:
            return entries

        if not 'include_' in comp:
            if '{' and '}' in comp:
                c_dict_lst = parse_formula_regex(comp)
                f_lst = []
                for cd in c_dict_lst:
                    f = ' '.join(['%s%g' % (k, cd[k]) for k in sorted(cd.keys())])
                    f_lst.append(f)
                entries = entries.filter(composition__formula__in=f_lst)
            else:
                c_lst = comp.strip().split('-')
                cs = Composition.get_list(c_lst)
                if len(cs) == 1:
                    c = cs[0]
                else:
                    c = cs
                entries = entries.filter(composition=c)

        else:
            comp_in = comp.replace('include_', '')
            t = Token(comp_in)
            q = t.evaluate()
            entries = entries.filter(q)

        #comp_ex = request.GET.get('composition_exclude', False)
        #if comp_ex:
        #    cex_lst = Composition.get(comp_ex).comp.keys()
        #    while cex_lst:
        #        tmp_ex = cex_lst.pop()
        #        entries = entries.exclude(composition__element_set=tmp_ex)

        return entries

    def calculated_filter(self, entries):
        request = self.request
        ifcalc = request.GET.get('calculated', True)
        
        if ifcalc in ['False', 'false', 'F', 'f']:
            return entries

        return entries.exclude(formationenergy=None)

    def bandgap_filter(self, entries):
        """
        Allowed syntax:
            1. ?band_gap=0
            2. ?band_gap=~0
            3. ?band_gap=>1.0
            4. ?band_gap=<2.0
        """
        request = self.request
        band_gap = request.GET.get('band_gap', False)
        
        if band_gap:
            calcs = Calculation.objects.filter(converged=True, label='static')
            if band_gap == '0':
                calcs = calcs.filter(band_gap=0)
            elif band_gap == '~0':
                calcs = calcs.exclude(band_gap=0)
            elif band_gap[0] == '<':
                gap_range = float(band_gap[1:])
                calcs = calcs.filter(band_gap__lt=gap_range)
            elif band_gap[0] == '>':
                gap_range = float(band_gap[1:])
                calcs = calcs.filter(band_gap__gt=gap_range)
            
            entries = entries.filter(calculation__in=calcs)

        return entries

    def ntypes_filter(self, entries):
        request = self.request
        ntypes = request.GET.get('ntypes', False)

        if ntypes:
            n = int(ntypes)
            entries = entries.filter(ntypes=n)

        return entries

    def generic_filter(self, entries):
        request = self.request
        generic = request.GET.get('generic', False)

        if generic:
            entries = entries.filter(composition__generic=generic)

        return entries

    def sort_by_bandgap(self, entries, sort_limit=100, sort_offset=0, desc=False):
        es_id = [e.id for e in entries]

        cs = Calculation.objects.filter(entry__id__in=es_id, 
                                        label='static')

        if desc in ['T', 't', 'True', 'true']:
            ordered_cs = cs.order_by('-band_gap')
        else:
            ordered_cs = cs.order_by('band_gap')
        return [c.entry for c in ordered_cs[sort_offset:sort_offset+sort_limit]]

    def sort_by_energyperatom(self, entries, sort_limit=100, sort_offset=0, desc=False):
        es_id = [e.id for e in entries]

        cs = Calculation.objects.filter(entry__id__in=es_id, 
                                        label='static')

        
        if desc in ['T', 't', 'True', 'true']:
            ordered_cs = cs.order_by('-energy_pa')
        else:
            ordered_cs = cs.order_by('energy_pa')
        return [c.entry for c in ordered_cs[sort_offset:sort_offset+sort_limit]]

    def sort_by_formationenergy(self, entries, sort_limit=100, sort_offset=0, desc=False):
        es_id = [e.id for e in entries]

        cs = Calculation.objects.filter(entry__id__in=es_id, 
                                        label='static')

        cs_id = [c.id for c in cs]

        fes = FormationEnergy.objects.filter(calculation_id__in=cs_id)

        
        if desc in ['T', 't', 'True', 'true']:
            ordered_fes = fes.order_by('-delta_e')
        else:
            ordered_fes = fes.order_by('delta_e')
        return [fe.entry for fe in ordered_fes[sort_offset:sort_offset+sort_limit]]

