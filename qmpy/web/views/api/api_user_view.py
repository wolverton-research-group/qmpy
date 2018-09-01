from django.contrib.auth.models import Group
from rest_framework import viewsets, generics
from qmpy.web.serializers.userinfo import APIUser, UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = APIUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class UserList(generics.ListAPIView):
    queryset = APIUser.objects.all()
    serializer_class = UserSerializer
