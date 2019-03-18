# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup_product_reviews"
    label = "shuup_product_reviews"
    verbose_name = "Shuup Product Reviews"
    provides = {
        "admin_module": [
            "shuup_product_reviews.admin_module.ProductReviewsModule"
        ],
        "xtheme_plugin": [
            "shuup_product_reviews.plugins.ProductReviewStarRatingsPlugin",
            "shuup_product_reviews.plugins.SupplierReviewStarRatingsPlugin",
            "shuup_product_reviews.plugins.ProductReviewCommentsPlugin",
            "shuup_product_reviews.plugins.SupplierReviewCommentsPlugin"
        ],
        "customer_dashboard_items": [
            "shuup_product_reviews.dashboard_items:ProductReviewDashboardItem"
        ],
        "front_urls": [
            "shuup_product_reviews.urls:urlpatterns"
        ],
        "xtheme_resource_injection": [
            "shuup_product_reviews.resources:add_resources"
        ]
    }
