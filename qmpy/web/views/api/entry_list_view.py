from rest_framework import generics
import django_filters.rest_framework
from qmpy.web.serializers.entry import EntrySerializer
from qmpy.materials.entry import Entry, Composition
from api_perm import *
from qmpy.utils import Token, parse_formula_regex

class EntryList(generics.ListAPIView):
    #permission_classes = (OnlyAPIPermission, )
    serializer_class = EntrySerializer
    #filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def get_queryset(self):
        entries = Entry.objects.all()
        entries = self.composition_filter(entries)
        entries = self.calculated_filter(entries)

        return entries

    def composition_filter(self, entries):
        """
        Valid url parameter inputs:
            1. ?composition=Fe2O3
            2. ?composition=Fe-O
            3. ?composition={Fe,Ni}O
            4. ?composition={3d}2O3
            5. ?composition_include=(Fe,Mn)-O : (Fe OR Mn) AND O
            6. ?composition_include=Cl,O-H : Cl OR O AND H 
            6. ?composition_include=H-{3d} : 3d elements AND H
        """
        request = self.request

        comp = request.GET.get('composition', False)
        if comp:
            if '{' and '}' in comp:
                c_dict_lst = parse_formula_regex(comp)
                f_lst = []
                for cd in c_dict_lst:
                    f = ' '.join(['%s%g' % (k, cd[k]) for k in sorted(cd.keys())])
                    f_lst.append(f)
                print f_lst
                entries = entries.filter(composition__formula__in=f_lst)
            else:
                c_lst = comp.strip().split('-')
                cs = Composition.get_list(c_lst)
                if len(cs) == 1:
                    c = cs[0]
                else:
                    c = cs
                entries = entries.filter(composition=c)

        comp_in = request.GET.get('composition_include', False)
        if comp_in:
            t = Token(comp_in)
            q = t.evaluate()
            entries = entries.filter(q)

        comp_ex = request.GET.get('composition_exclude', False)
        if comp_ex:
            cex_lst = Composition.get(comp_ex).comp.keys()
            while cex_lst:
                tmp_ex = cex_lst.pop()
                entries = entries.exclude(composition__element_set=tmp_ex)

        return entries

    def calculated_filter(self, entries):
        request = self.request
        ifcalc = request.GET.get('calculated', True)
        
        if ifcalc == 'False':
            return entries

        return entries.exclude(formationenergy=None)

