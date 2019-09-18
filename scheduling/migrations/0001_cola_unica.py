# Generated by Django 2.2.2 on 2019-09-18 06:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('scheduling', '0001_initial'), ('scheduling', '0002_auto_20190801_1943'), ('scheduling', '0003_colacargapendientes'), ('scheduling', '0004_cola_cargas_pendientes'), ('scheduling', '0005_auto_20190918_0213'), ('scheduling', '0006_remove_colacargaspendientes_attachment'), ('scheduling', '0007_colacargaspendientes_attachment'), ('scheduling', '0008_auto_20190918_0221'), ('scheduling', '0009_auto_20190918_0243'), ('scheduling', '0010_auto_20190918_0247')]

    initial = True

    dependencies = [
        ('elecciones', '0057_auto_20190901_1444'),
        ('adjuntos', '0014_reemplazo_taken'),
        ('elecciones', '0037_auto_20190727_1136'),
        ('elecciones', '0059_merge_20190910_0847'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrioridadScheduling',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desde_proporcion', models.PositiveIntegerField()),
                ('hasta_proporcion', models.PositiveIntegerField()),
                ('prioridad', models.PositiveIntegerField(null=True)),
                ('hasta_cantidad', models.PositiveIntegerField(null=True)),
                ('categoria', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prioridades', to='elecciones.Categoria')),
                ('seccion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prioridades', to='elecciones.Seccion')),
            ],
        ),
        migrations.CreateModel(
            name='ColaCargasPendientes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orden', models.PositiveIntegerField(db_index=True)),
                ('mesa_categoria', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='elecciones.MesaCategoria')),
                ('attachment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='adjuntos.Attachment')),
                ('numero_carga', models.PositiveIntegerField(default=1)),
            ],
            options={
                'unique_together': {('mesa_categoria', 'numero_carga')},
            },
        ),
    ]
