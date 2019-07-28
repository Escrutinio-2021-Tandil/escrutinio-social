from django.urls import reverse
from http import HTTPStatus

from elecciones.tests.factories import (
    FiscalFactory,
    SeccionFactory,
)
from fiscales.models import Fiscal


QUIERO_SER_FISCAL_REQUEST_DATA_DEFAULT = {
    "nombres": "Diego Armando",
    "apellido": "Maradona",
    "dni": "14276579",
    "distrito": "1",
    "referente_nombres": "Hugo Rafael",
    "referente_apellido": "Chavez",
    "referido_por_codigo": "BLVR",
    "telefono_local": "42631145",
    "telefono_area": "11",
    "email": "diego@maradona.god.ar",
    "email_confirmacion": "diego@maradona.god.ar",
    "password": "diego1986",
    "password_confirmacion": "diego1986",
}


def test_quiero_validar__camino_feliz(db, client):
    url_quiero_validar = reverse('quiero-validar')
    response = client.get(url_quiero_validar)
    assert response.status_code == HTTPStatus.OK

    assert not Fiscal.objects.exists()

    seccion = SeccionFactory()
    request_data = construir_request_data(seccion)
    response = client.post(url_quiero_validar, request_data)

    assert Fiscal.objects.count() == 1
    _assert_fiscal_cargado_correctamente(seccion)

    fiscal = _get_fiscal()
    url_gracias = reverse('quiero-validar-gracias', kwargs={'codigo_ref': fiscal.referido_por_codigos})

    assert HTTPStatus.FOUND == response.status_code
    assert url_gracias == response.url


def test_quiero_validar__error_validacion(db, client):
    # hacemos un test que muestre que al validar nos quedamos en la misma página y no se crea un fiscal
    # la lógica de validación más fina del form la hacemos en el test_forms_fiscales
    url_quiero_validar = reverse('quiero-validar')
    response = client.get(url_quiero_validar)
    assert response.status_code == HTTPStatus.OK

    assert not Fiscal.objects.exists()

    seccion = SeccionFactory()
    request_data = construir_request_data(seccion)
    del(request_data["dni"])
    response = client.post(url_quiero_validar, request_data)

    assert response.status_code == HTTPStatus.OK
    assert response.context['form'].errors

    assert not Fiscal.objects.exists()


def _get_fiscal():
    return Fiscal.objects.filter(
        referido_por_codigos=QUIERO_SER_FISCAL_REQUEST_DATA_DEFAULT['referido_por_codigo']
    ).first()


def _assert_fiscal_cargado_correctamente(seccion):
    fiscal = _get_fiscal()

    assert fiscal
    assert len(fiscal.referido_por_codigos) == 4

    assert fiscal.nombres == QUIERO_SER_FISCAL_REQUEST_DATA_DEFAULT['nombres']
    assert fiscal.apellido == QUIERO_SER_FISCAL_REQUEST_DATA_DEFAULT['apellido']
    assert fiscal.dni == QUIERO_SER_FISCAL_REQUEST_DATA_DEFAULT['dni']

    assert fiscal.seccion == seccion

    assert fiscal.referente_apellido == QUIERO_SER_FISCAL_REQUEST_DATA_DEFAULT['referente_apellido']
    assert fiscal.referente_nombres == QUIERO_SER_FISCAL_REQUEST_DATA_DEFAULT['referente_nombres']
    assert fiscal.referido_por_codigos == QUIERO_SER_FISCAL_REQUEST_DATA_DEFAULT['referido_por_codigo']

    assert QUIERO_SER_FISCAL_REQUEST_DATA_DEFAULT['telefono_local'] in fiscal.telefonos[0]
    assert fiscal.telefonos[0].startswith(QUIERO_SER_FISCAL_REQUEST_DATA_DEFAULT['telefono_area'])

    assert fiscal.user is not None
    assert fiscal.user.password is not None


def construir_request_data(seccion):
    data = QUIERO_SER_FISCAL_REQUEST_DATA_DEFAULT.copy()
    data["seccion"] = seccion.id
    data["seccion_autocomplete"] = seccion.id
    return data
