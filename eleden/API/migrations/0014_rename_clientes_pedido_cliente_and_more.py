# Generated by Django 4.2.9 on 2024-10-15 18:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0013_detalleventa_venta_remove_itemcompra_compra_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pedido',
            old_name='clientes',
            new_name='cliente',
        ),
        migrations.RemoveField(
            model_name='pedido',
            name='cantidad',
        ),
        migrations.RemoveField(
            model_name='pedido',
            name='precio_unitario',
        ),
        migrations.RemoveField(
            model_name='pedido',
            name='productos',
        ),
        migrations.AlterField(
            model_name='pedido',
            name='precio_total',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.CreateModel(
            name='PedidoProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField()),
                ('precio_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productos', to='API.pedido')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.productoterminado')),
            ],
        ),
    ]
