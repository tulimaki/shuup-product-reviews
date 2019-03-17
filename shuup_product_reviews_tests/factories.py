# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import random
from uuid import uuid4

from faker import Faker

from shuup.core.models import OrderStatus
from shuup.testing import factories
from shuup_product_reviews.models import ProductReview, ReviewStatus


def create_random_review_for_product(shop, product, reviewer=None, order=None, approved=True,
                                     rating=None, would_recommend=None, generate_comment=True):
    if reviewer is None:
        reviewer = factories.create_random_person("en")

    if order is None:
        order = factories.create_order_with_product(
            product=product,
            supplier=factories.get_default_supplier(),
            quantity=1,
            taxless_base_unit_price=10,
            shop=shop
        )

    order_line = order.lines.filter(product=product).first()
    if not order_line:
        order_line = order.lines().first()

    if rating is None:
        rating = random.randint(1, 5)

    if would_recommend is None:
        would_recommend = random.choice([True, False])

    comment = None
    if generate_comment:
        comment = Faker().text(100)

    return ProductReview.objects.create(
        shop=shop,
        product=product,
        reviewer=reviewer,
        order_line=order_line,
        rating=rating,
        comment=comment,
        would_recommend=would_recommend,
        status=(ReviewStatus.APPROVED if approved else ReviewStatus.PENDING)
    )


def create_random_review_for_reviwer(shop, reviewer, order=None, approved=True,
                                     rating=None, would_recommend=None, generate_comment=True):
    if reviewer is None:
        reviewer = factories.create_random_person("en")

    product = factories.create_product(uuid4().hex, shop=shop, supplier=factories.get_default_supplier())

    if order is None:
        order = factories.create_order_with_product(
            product=product,
            supplier=factories.get_default_supplier(),
            quantity=1,
            taxless_base_unit_price=10,
            shop=shop
        )

    order_line = order.lines.filter(product=product).first()
    if not order_line:
        order_line = order.lines().first()

    if rating is None:
        rating = random.randint(1, 5)

    if would_recommend is None:
        would_recommend = random.choice([True, False])

    comment = None
    if generate_comment:
        comment = Faker().text(100)

    return ProductReview.objects.create(
        shop=shop,
        product=product,
        reviewer=reviewer,
        order_line=order_line,
        rating=rating,
        comment=comment,
        would_recommend=would_recommend,
        status=(ReviewStatus.APPROVED if approved else ReviewStatus.PENDING)
    )


def create_random_order_to_review(shop, customer):
    order = factories.create_order_with_product(
        product=factories.create_product(uuid4().hex, shop=shop, supplier=factories.get_default_supplier()),
        supplier=factories.get_default_supplier(),
        quantity=1,
        taxless_base_unit_price=10,
        shop=shop
    )
    order.customer = customer
    order.create_payment(order.taxful_total_price)
    order.create_shipment_of_all_products(factories.get_default_supplier())
    order.status = OrderStatus.objects.get_default_complete()
    order.save()
    return order


def create_multi_supplier_order_to_review(shop_product, customer):
    order = factories.create_empty_order(shop=shop_product.shop)
    order.full_clean()
    order.save()

    pricing_context = factories._get_pricing_context(order.shop, order.customer)
    for supplier in shop_product.suppliers.all():
        factories.add_product_to_order(
            order, supplier, shop_product.product, 1, shop_product.default_price_value, 0, pricing_context
        )

    order.cache_prices()
    order.save()

    order.customer = customer
    order.create_payment(order.taxful_total_price)
    for supplier in shop_product.suppliers.all():
        order.create_shipment_of_all_products(supplier)
    order.status = OrderStatus.objects.get_default_complete()
    order.save()

    return order
