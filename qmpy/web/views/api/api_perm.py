from rest_framework import permissions
from qmpy.apis.api_key import APIKey

class OnlyAPIPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            api_key = request.GET.get('apikey', False)
            APIKey.objects.get(key=api_key)
            return True
        except:
            return False
