# Generated by Django 5.1.1 on 2024-10-05 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0003_alter_orderitem_product"),
    ]

    operations = [
        migrations.AddField(
            model_name="repairorder",
            name="code",
            field=models.CharField(blank=True, max_length=12, null=True, unique=True),
        ),
    ]
