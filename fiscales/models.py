import re
import uuid
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models import Sum
from django.db.models.signals import post_save, pre_delete
from elecciones.models import Seccion
from django.contrib.contenttypes.models import ContentType
from contacto.models import DatoDeContacto
from model_utils.fields import StatusField
from model_utils import Choices
from django.contrib.auth.models import Group

from antitrolling.models import (
    registrar_fiscal_no_es_troll, marcar_fiscal_troll, EventoScoringTroll, crear_evento_marca_explicita_como_troll
)
from antitrolling.efecto import efecto_determinacion_fiscal_troll

TOTAL = 'Total General'


class Fiscal(models.Model):
    """
    Representa al usuario "data-entry" del sistema.
    Es una extensión del modelo ``auth.User``

    """
    TIPO_DNI = Choices('DNI', 'CI', 'LE', 'LC')
    ESTADOS = Choices('IMPORTADO', 'AUTOCONFIRMADO', 'PRE-INSCRIPTO', 'CONFIRMADO', 'DECLINADO')

    # Actualmente no se consideran los diferentes estados
    # salvo para la creación del user asociado.
    estado = StatusField(choices_name='ESTADOS', default='PRE-INSCRIPTO')
    notas = models.TextField(blank=True, help_text='Notas internas, no se muestran')
    codigo_confirmacion = models.UUIDField(default=uuid.uuid4, editable=False)
    email_confirmado = models.BooleanField(default=False)
    apellido = models.CharField(max_length=50)
    nombres = models.CharField(max_length=100)
    tipo_dni = models.CharField(choices=TIPO_DNI, max_length=3, default='DNI')
    dni = models.CharField(max_length=15, blank=True, null=True)
    datos_de_contacto = GenericRelation('contacto.DatoDeContacto', related_query_name='fiscales')
    troll = models.BooleanField(null=False, default=False)
    user = models.OneToOneField(
        'auth.User', null=True, blank=True, related_name='fiscal', on_delete=models.SET_NULL
    )
    seccion = models.ForeignKey(Seccion, related_name='fiscal', null=True, blank=True, on_delete=models.SET_NULL)
    referido_codigo = models.CharField(max_length=4, blank=True, null=True, unique=True)
    referido_por_nombres = models.CharField(max_length=100, blank=True, null=True)
    referido_por_apellido = models.CharField(max_length=100, blank=True, null=True)
    referido_por_codigo = models.CharField(max_length=4, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Fiscales'
        unique_together = (('tipo_dni', 'dni'), )

    def agregar_dato_de_contacto(self, tipo, valor):
        type_ = ContentType.objects.get_for_model(self)
        try:
            DatoDeContacto.objects.get(content_type__pk=type_.id, object_id=self.id, tipo=tipo, valor=valor)
        except DatoDeContacto.DoesNotExist:
            DatoDeContacto.objects.create(content_object=self, tipo=tipo, valor=valor)

    @property
    def telefonos(self):
        return self.datos_de_contacto.filter(tipo='teléfono').values_list('valor', flat=True)

    @property
    def emails(self):
        return self.datos_de_contacto.filter(tipo='email').values_list('valor', flat=True)

    def __str__(self):
        return f'{self.nombres} {self.apellido}'

    def esta_en_grupo(self, nombre_grupo):
        grupo = Group.objects.get(name=nombre_grupo)

        return grupo in self.user.groups.all()

    def esta_en_algun_grupo(self, nombres_grupos):
        for nombre in nombres_grupos:
            try:
                grupo = Group.objects.get(name=nombre)
                if grupo in self.user.groups.all():
                    return True
            except Group.DoesNotExist:
                continue
        return False

    # Especializaciones para usar desde los templates.
    @property
    def esta_en_grupo_validadores(self):
        return self.esta_en_grupo('validadores')

    @property
    def esta_en_grupo_visualizadores(self):
        return self.esta_en_grupo('visualizadores')

    @property
    def esta_en_grupo_unidades_basicas(self):
        return self.esta_en_grupo('unidades basicas')
        
    def scoring_troll(self):
        return self.eventos_scoring_troll.aggregate(v=Sum('variacion'))['v'] or 0

    def marcar_como_troll(self, actor):
        """
        Un UE decidió, explícitamente, marcarme como troll
        """
        evento = crear_evento_marca_explicita_como_troll(self, actor)
        marcar_fiscal_troll(self, evento)

    def aplicar_marca_troll(self):
        """
        Ejecutar las consecuencias de la decisión de marcarme como troll.
        La decisión puede ser automática o manual.
        El código que refleja la decisión generó el CambioEstadoTroll correspondiente,
        este método es para el resto de las consecuencias.
        """
        self.troll = True
        self.save(update_fields=['troll'])
        efecto_determinacion_fiscal_troll(self)

    def quitar_marca_troll(self, actor, nuevo_scoring):
        """
        Un UE decidió, explícitamente, quitarme la marca de troll.
        Este es el único caso en que un fiscal pierde la marca de troll, no hay eventos automáticos para esto.
        Por eso este método incluye todas las consecuencias del acto de desmarcar, 
        al contrario de la decisión de marcar que puede ser manual o automática.
        """
        era_troll = self.troll
        self.troll = False
        self.save(update_fields=['troll'])
        if (era_troll):
            registrar_fiscal_no_es_troll(self, nuevo_scoring, actor)




@receiver(post_save, sender=Fiscal)
def crear_user_para_fiscal(sender, instance=None, created=False, **kwargs):
    """
    Cuando se crea o actualiza una instancia de ``Fiscal`` en estado confirmado
    que no tiene usuario asociado, automáticamente se crea uno ``auth.User``
    utilizando el DNI como `username`.
    """
    if not instance.user and instance.dni and instance.estado in ('AUTOCONFIRMADO', 'CONFIRMADO'):
        user = User(
            username=re.sub("[^0-9]", "", instance.dni),
            first_name=instance.nombres,
            last_name=instance.apellido,
            is_active=True,
            email=instance.emails[0] if instance.emails else ""
        )

        # user.set_password(settings.DEFAULT_PASS_PREFIX + instance.dni[-3:])
        user.save()
        instance.user = user
        instance.save(update_fields=['user'])


@receiver(pre_delete, sender=Fiscal)
def borrar_user_para_fiscal(sender, instance=None, **kwargs):
    if instance.user:
        instance.user.delete()
