# Generated by Django 4.2.9 on 2024-10-15 02:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0012_itemcompra'),
    ]

    operations = [
        migrations.CreateModel(
            name='DetalleVenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('precio_historico', models.IntegerField()),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='API.ventasoftware')),
            ],
        ),
        migrations.CreateModel(
            name='Venta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_venta', models.DateTimeField(auto_now=True)),
                ('estado', models.IntegerField(choices=[(1, 'Pendiente'), (2, 'Enviado'), (3, 'Rechazada')], default=1)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='itemcompra',
            name='compra',
        ),
        migrations.RemoveField(
            model_name='itemcompra',
            name='venta_software',
        ),
        migrations.DeleteModel(
            name='Compra',
        ),
        migrations.DeleteModel(
            name='ItemCompra',
        ),
        migrations.AddField(
            model_name='detalleventa',
            name='venta',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='API.venta'),
        ),
    ]
