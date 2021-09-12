from elecciones.models import Mesa, MesaCategoria
from api.serializers import MesaDasboardSerializer

from rest_framework import viewsets


class mesas_dashboard(viewsets.ModelViewSet):
  queryset = Mesa.objects.all()
  serializer_class = MesaDasboardSerializer
  pagination_class = None
