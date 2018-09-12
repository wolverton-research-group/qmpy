from rest_framework import generics
import django_filters.rest_framework
from qmpy.web.serializers.entry import EntrySerializer
from qmpy.materials.entry import Entry, Composition
from api_perm import *

class EntryList(generics.ListAPIView):
    #permission_classes = (OnlyAPIPermission, )
    serializer_class = EntrySerializer
    #filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def get_queryset(self):
        entries = Entry.objects.all()
        entries = self.composition_filter(entries)

        return entries

    def composition_filter(self, entries):
        request = self.request

        comp = request.GET.get('composition', False)
        if comp:
            c_lst = comp.strip().split('-')
            cs = Composition.get_list(c_lst, calculated=True)
            if len(cs) == 1:
                c = cs[0]
            else:
                c = cs
            entries = entries.filter(composition=c)

        comp_in = request.GET.get('composition_include', False)
        if comp_in:
            cin_lst = Composition.get(comp_in).comp.keys()
            while cin_lst:
                tmp_in = cin_lst.pop()
                entries = entries.filter(composition__element_set=tmp_in)

        comp_ex = request.GET.get('composition_exclude', False)
        if comp_ex:
            cex_lst = Composition.get(comp_ex).comp.keys()
            while cex_lst:
                tmp_ex = cex_lst.pop()
                entries = entries.exclude(composition__element_set=tmp_ex)

        return entries
