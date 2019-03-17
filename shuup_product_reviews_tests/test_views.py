# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import json
import random

import pytest
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.client import Client
from faker import Faker

from shuup.core.models import Supplier
from shuup.testing import factories
from shuup.testing.soup_utils import extract_form_fields

from .factories import (
    create_multi_supplier_order_to_review, create_random_order_to_review,
    create_random_review_for_product, create_random_review_for_reviwer
)


class SmartClient(Client):
    def soup(self, path, data=None, method="get"):
        response = getattr(self, method)(path=path, data=data)
        assert 200 <= response.status_code <= 299, "Valid status"
        return BeautifulSoup(response.content)

    def response_and_soup(self, path, data=None, method="get"):
        response = getattr(self, method)(path=path, data=data)
        return (response, BeautifulSoup(response.content))


@pytest.mark.django_db
def test_reviews_view(rf):
    shop = factories.get_default_shop()
    customer = factories.create_random_person("en")
    user = factories.create_random_user("en")
    user.set_password("user")
    user.save()
    customer.user = user
    customer.save()

    client = SmartClient()
    client.login(username=user.username, password="user")

    # no reviews in dashboard
    response = client.get(reverse("shuup:dashboard"))
    assert response.status_code == 200
    response.render()
    content = response.content.decode("utf-8")
    assert "You haven't made any reviews yet" in content

    # create some reviews for customer
    [create_random_review_for_reviwer(shop, customer) for _ in range(15)]
    # create some orders to review
    [create_random_order_to_review(shop, customer) for order in range(3)]

    # reload dashboard
    response = client.get(reverse("shuup:dashboard"))
    assert response.status_code == 200
    response.render()
    content = response.content.decode("utf-8")
    assert "Last reviews" in content

    # show all reviews
    response, soup = client.response_and_soup(reverse("shuup:product_reviews"))
    assert response.status_code == 200
    response.render()
    content = response.content.decode("utf-8")
    assert "Products to Review" in content

    form_data = extract_form_fields(soup)

    for key in form_data.keys():
        if key.endswith("comment"):
            form_data[key] = Faker().text(100)
        if key.endswith("rating"):
            form_data[key] = random.randint(1, 5)
        if key.endswith("would_recommend"):
            form_data[key] = random.choice([True, False])

    # post reviews
    request = rf.post("/")
    request.person = request.customer = customer
    request.shop = shop

    response = client.post(reverse("shuup:product_reviews"), data=form_data)
    assert response.status_code == 302

    response = client.get(reverse("shuup:product_reviews"))
    assert response.status_code == 200
    response.render()
    content = response.content.decode("utf-8")
    assert "Products to Review" not in content


@pytest.mark.django_db
def test_reviews_view_multiple_supplires(rf):
    shop = factories.get_default_shop()
    customer = factories.create_random_person("en")
    user = factories.create_random_user("en")
    user.set_password("user")
    user.save()
    customer.user = user
    customer.save()

    supplier1_name = "Supplier 1 name"
    supplier1 = Supplier.objects.create(identifier="1", name=supplier1_name)
    supplier2_name = "Supplier 2 name"
    supplier2 = Supplier.objects.create(identifier="2", name=supplier2_name)
    product = factories.create_product("test1", shop=shop, supplier=supplier1, default_price=10)
    shop_product = product.get_shop_instance(shop=shop)
    assert shop_product.suppliers.filter(id=supplier1.id).exists()
    shop_product.suppliers.add(supplier2)
    assert shop_product.suppliers.filter(id=supplier2.id).exists()

    create_multi_supplier_order_to_review(shop_product, customer)

    client = SmartClient()
    client.login(username=user.username, password="user")

    # show all pending reviews which would be 1 for each supplier
    response, soup = client.response_and_soup(reverse("shuup:product_reviews"))
    assert "Products to Review" in soup.text
    assert len(soup.findAll("tbody")[0].findChildren("tr")) == 2
    assert "(%s)" % supplier2_name in soup.text
    assert "(%s)" % supplier1_name in soup.text


@pytest.mark.django_db
def test_comments_view():
    shop = factories.get_default_shop()
    product = factories.create_product("product", shop=shop, supplier=factories.get_default_supplier())
    client = Client()

    # create 15 reviews for the product, it should exist 3 pages of comments
    [create_random_review_for_product(shop, product) for _ in range(15)]

    # load first page of comments
    response = client.get(reverse("shuup:product_review_comments", kwargs=dict(pk=product.pk)))
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert len(data["reviews"]) == settings.PRODUCT_REVIEWS_PAGE_SIZE
    assert data["next_page_url"]

    # request next page
    response = client.get(data["next_page_url"])
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert len(data["reviews"]) == settings.PRODUCT_REVIEWS_PAGE_SIZE
    assert data["next_page_url"]

    # request next page
    response = client.get(data["next_page_url"])
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert len(data["reviews"]) == settings.PRODUCT_REVIEWS_PAGE_SIZE
    # no more pages
    assert data["next_page_url"] is None

    # request a page that doesn't exist (too far) - it should return the last page
    url = "{}?page=999999".format(reverse("shuup:product_review_comments", kwargs=dict(pk=product.pk)))
    response = client.get(url)
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert len(data["reviews"]) == settings.PRODUCT_REVIEWS_PAGE_SIZE
    # no more pages
    assert data["next_page_url"] is None
