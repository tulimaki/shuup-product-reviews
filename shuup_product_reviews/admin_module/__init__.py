# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.menu import PRODUCTS_MENU_CATEGORY
from shuup.admin.utils.urls import admin_url


class ProductReviewsModule(AdminModule):
    name = _("Product Reviews")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:product_reviews.list")

    def get_urls(self):
        return [
            admin_url(
                r"^product_reviews/$",
                "shuup_product_reviews.admin_module.views.ProductReviewListView",
                name="product_reviews.list"
            ),
            admin_url(
                r"^product_reviews/list-settings/",
                "shuup.admin.modules.settings.views.ListSettingsView",
                name="product_reviews.list_settings"
            )
        ]

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-star",
                url="shuup_admin:product_reviews.list",
                category=PRODUCTS_MENU_CATEGORY,
                subcategory="products",
                ordering=5
            )
        ]


class SupplierReviewsModule(AdminModule):
    name = _("Vendor Reviews")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:vendor_reviews.list")

    def get_urls(self):
        return [
            admin_url(
                r"^vendor_reviews/$",
                "shuup_product_reviews.admin_module.views.VendorReviewListView",
                name="vendor_reviews.list"
            ),
            admin_url(
                r"^vendor_reviews/list-settings/",
                "shuup.admin.modules.settings.views.ListSettingsView",
                name="vendor_reviews.list_settings"
            )
        ]

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-star",
                url="shuup_admin:vendor_reviews.list",
                category=PRODUCTS_MENU_CATEGORY,
                subcategory="products",
                ordering=6
            )
        ]
