from rest_framework import generics
import django_filters.rest_framework
from qmpy.web.serializers.calculation import CalculationSerializer
from qmpy.analysis.vasp import Calculation

class CalculationDetail(generics.RetrieveAPIView):
    queryset = Calculation.objects.all()
    serializer_class = CalculationSerializer

class CalculationList(generics.ListAPIView):
    serializer_class = CalculationSerializer

    def get_queryset(self):
        calcs = Calculation.objects.all()
        calcs = self.label_filter(calcs)
        calcs = self.converged_filter(calcs)
        calcs = self.band_gap_filter(calcs)

        return calcs

    def label_filter(self, calcs):
        request = self.request
        label = request.GET.get('label', False)

        if label:
            calcs = calcs.filter(label=label)

        return calcs

    def converged_filter(self, calcs):
        request = self.request
        converged = request.GET.get('converged', False)

        if converged:
            if converged in ['False', 'false', 'f', 'F']:
                converged_filter = False
            elif converged in ['True', 'true', 't', 'T']:
                converged_filter = True

            calcs = calcs.filter(converged=converged_filter)

        return calcs

    def band_gap_filter(self, calcs):
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

        return calcs
