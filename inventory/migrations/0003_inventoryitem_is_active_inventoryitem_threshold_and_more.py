# Generated by Django 5.1.1 on 2024-10-10 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_remove_product_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventoryitem',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='threshold',
            field=models.PositiveIntegerField(default=10),
        ),
        migrations.AddField(
            model_name='inventorytransfer',
            name='expected_transfer_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='inventorytransfer',
            name='reason',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='warehouse',
            name='capacity',
            field=models.PositiveIntegerField(default=10000),
        ),
        migrations.AlterField(
            model_name='inventorytransfer',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], max_length=50),
        ),
    ]