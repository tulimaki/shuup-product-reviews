# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-18 01:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shuup', '0057_remove_product_stock_behavior'),
        ('shuup_product_reviews', '0003_unnullify_order_line'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupplierReviewAggregation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.DecimalField(decimal_places=1, default=0, max_digits=2, verbose_name='rating')),
                ('review_count', models.PositiveIntegerField(default=0, verbose_name='review count')),
                ('supplier', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='supplier_reviews_aggregation', to='shuup.Supplier', verbose_name='supplier')),
            ],
        )
    ]
