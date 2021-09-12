from rest_framework.permissions import IsAuthenticated

from elecciones.models import Mesa, MesaCategoria
from api.serializers import MesaDasboardSerializer

from rest_framework import viewsets


class mesas_dashboard(viewsets.ModelViewSet):
  permission_classes = (IsAuthenticated,)
  queryset = Mesa.objects.all()
  serializer_class = MesaDasboardSerializer
  pagination_class = None
