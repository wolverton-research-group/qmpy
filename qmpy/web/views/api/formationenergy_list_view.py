from rest_framework import generics
import django_filters.rest_framework
from qmpy.web.serializers.formationenergy import FormationEnergySerializer
from qmpy.materials.formation_energy import FormationEnergy
from api_perm import *
from qmpy.utils import Token, parse_formula_regex

DEFAULT_LIMIT = 50

class FormationEnergyDetail(generics.RetrieveAPIView):
    queryset = FormationEnergy.objects.all()
    serializer_class = FormationEnergySerializer

class FormationEnergyList(generics.ListAPIView):
    #permission_classes = (OnlyAPIPermission, )
    serializer_class = FormationEnergySerializer
    #filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def get_queryset(self):
        fes = FormationEnergy.objects.filter(fit="standard")
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

    def filter(self, fes):
        request = self.request
        return fes

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

    def sort_by_stability(self, fes, limit=DEFAULT_LIMIT, sort_offset=0, desc=False):
        if desc in ['T', 't', 'True', 'true']:
            ordered_fes = fes.order_by('-stability')
        else:
            ordered_fes = fes.order_by('stability')
        return ordered_fes[sort_offset:sort_offset+limit]
