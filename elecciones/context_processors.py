from elecciones.models import Mesa, Eleccion
from adjuntos.models import Attachment

from django.utils.cache import add_never_cache_headers


class DisableClientSideCachingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        add_never_cache_headers(response)
        return response



def contadores(request):
    e = Eleccion.objects.first()
    return {
        'adjuntos_count': Attachment.sin_asignar().count(),
        'mesas_pendientes_count': Mesa.con_carga_pendiente().count(),
        'mesas_a_confirmar_count': Mesa.con_carga_a_confirmar().count(),

        'primera_eleccion': e.id if e is not None else 1   # las urls esperan un entero.
                                                           # aunque no exista el objeto
    }
