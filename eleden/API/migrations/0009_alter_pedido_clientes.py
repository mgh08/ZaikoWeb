# Generated by Django 4.2.9 on 2024-10-08 00:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0008_remove_materiaprima_proveedores_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='clientes',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='API.cliente'),
            preserve_default=False,
        ),
    ]