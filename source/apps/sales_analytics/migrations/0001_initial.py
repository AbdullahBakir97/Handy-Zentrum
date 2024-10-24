# Generated by Django 5.1.1 on 2024-09-24 16:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SalesReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("report_date", models.DateField(auto_now_add=True)),
                ("total_sales", models.DecimalField(decimal_places=2, max_digits=10)),
                ("total_orders", models.PositiveIntegerField()),
                ("total_customers", models.PositiveIntegerField()),
                (
                    "average_order_value",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "highest_selling_product",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="highest_selling_product",
                        to="inventory.product",
                    ),
                ),
            ],
            options={
                "verbose_name": "Sales Report",
                "verbose_name_plural": "Sales Reports",
                "ordering": ["-report_date"],
            },
        ),
        migrations.CreateModel(
            name="SalesByProduct",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("total_units_sold", models.PositiveIntegerField()),
                ("total_revenue", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sales_data",
                        to="inventory.product",
                    ),
                ),
                (
                    "report",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sales_by_product",
                        to="sales_analytics.salesreport",
                    ),
                ),
            ],
            options={
                "verbose_name": "Sales by Product",
                "verbose_name_plural": "Sales by Product",
                "ordering": ["-total_units_sold"],
            },
        ),
        migrations.CreateModel(
            name="SalesByCustomerSegment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("segment", models.CharField(max_length=100)),
                ("total_sales", models.DecimalField(decimal_places=2, max_digits=10)),
                ("total_orders", models.PositiveIntegerField()),
                (
                    "report",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sales_by_segment",
                        to="sales_analytics.salesreport",
                    ),
                ),
            ],
            options={
                "verbose_name": "Sales by Customer Segment",
                "verbose_name_plural": "Sales by Customer Segments",
                "ordering": ["segment"],
            },
        ),
        migrations.AddIndex(
            model_name="salesreport",
            index=models.Index(
                fields=["report_date"], name="sales_analy_report__93510e_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="salesbyproduct",
            constraint=models.CheckConstraint(
                condition=models.Q(("total_units_sold__gte", 0)),
                name="total_units_non_negative",
            ),
        ),
        migrations.AddConstraint(
            model_name="salesbyproduct",
            constraint=models.CheckConstraint(
                condition=models.Q(("total_revenue__gte", 0)),
                name="total_revenue_non_negative",
            ),
        ),
        migrations.AddConstraint(
            model_name="salesbycustomersegment",
            constraint=models.CheckConstraint(
                condition=models.Q(("total_sales__gte", 0)),
                name="total_sales_non_negative",
            ),
        ),
        migrations.AddConstraint(
            model_name="salesbycustomersegment",
            constraint=models.CheckConstraint(
                condition=models.Q(("total_orders__gte", 0)),
                name="total_orders_non_negative",
            ),
        ),
    ]
