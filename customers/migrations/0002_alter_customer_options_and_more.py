# Generated by Django 5.1.1 on 2024-09-18 10:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'ordering': ['-date_joined'], 'verbose_name': 'Customer', 'verbose_name_plural': 'Customers'},
        ),
        migrations.AlterModelOptions(
            name='customerinteraction',
            options={'ordering': ['-interaction_date'], 'verbose_name': 'Customer Interaction', 'verbose_name_plural': 'Customer Interactions'},
        ),
        migrations.AlterModelOptions(
            name='loyaltyprogram',
            options={'verbose_name': 'Loyalty Program', 'verbose_name_plural': 'Loyalty Programs'},
        ),
        migrations.RemoveField(
            model_name='customer',
            name='address',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='city',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='country',
        ),
        migrations.AddField(
            model_name='customer',
            name='loyalty_tier_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_type', models.CharField(choices=[('billing', 'Billing'), ('shipping', 'Shipping')], max_length=20)),
                ('address_line_1', models.CharField(max_length=255)),
                ('address_line_2', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(max_length=100)),
                ('country', models.CharField(max_length=100)),
                ('postal_code', models.CharField(max_length=20)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='customers.customer')),
            ],
            options={
                'verbose_name': 'Address',
                'verbose_name_plural': 'Addresses',
            },
        ),
    ]