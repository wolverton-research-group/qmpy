from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from qmpy.web.serializers.entry import EntrySerializer
from qmpy.materials.entry import Entry

class EntryList(APIView):
    def get(self, request, format=None):
        entries = Entry.objects.all()[:10]
        serializer = EntrySerializer(entries, many=True)
        return Response(serializer.data)

#@api_view(['GET'])
#def get_entry_list(request):
#    if request.method == 'GET':
#        entries = Entry.objects.all()[:10]
#        serializer = EntrySerializer(entries, many=True)
#        return Response(serializer.data)
