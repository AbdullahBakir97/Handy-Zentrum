# Generated by Django 5.1.1 on 2024-09-24 17:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("carts", "0001_initial"),
        ("customers", "0001_initial"),
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="cartcoupon",
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name="cartitem",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="cart",
            name="total_quantity",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="cartitem",
            name="quantity",
            field=models.PositiveIntegerField(
                default=1, validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
        migrations.AddConstraint(
            model_name="cart",
            constraint=models.CheckConstraint(
                condition=models.Q(("total_quantity__gte", 0)),
                name="cart_quantity_non_negative",
            ),
        ),
        migrations.AddConstraint(
            model_name="cartcoupon",
            constraint=models.UniqueConstraint(
                fields=("cart", "code"), name="unique_cart_coupon"
            ),
        ),
        migrations.AddConstraint(
            model_name="cartitem",
            constraint=models.UniqueConstraint(
                fields=("cart", "product"), name="unique_cart_product"
            ),
        ),
    ]
