# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from shuup.admin.shop_provider import get_shop
from shuup.admin.utils.picotable import (
    ChoicesFilter, Column, RangeFilter, TextFilter
)
from shuup.admin.utils.views import PicotableListView
from shuup.utils import djangoenv
from shuup_product_reviews.models import ProductReview, ReviewStatus


class BaseProductReviewListView(PicotableListView):
    model = ProductReview

    default_columns = [
        Column(
            "product",
            _("Product"),
            filter_config=TextFilter(
                filter_field="product__translations__name",
                placeholder=_("Filter by product...")
            )
        ),
        Column(
            "reviewer__name",
            _("Reviewer"),
            filter_config=TextFilter(filter_field="reviewer__name")
        ),
        Column(
            "rating",
            _("Rating"),
            filter_config=RangeFilter(min=1, max=5, step=1, filter_field="rating")
        ),
        Column("comment", _("Comment")),
        Column(
            "status",
            _("Status"),
            filter_config=ChoicesFilter(
                choices=ReviewStatus.choices(),
                filter_field="status"
            )
        )
    ]


class ProductReviewListView(BaseProductReviewListView):
    url_identifier = "product_reviews"

    mass_actions = [
        "shuup_product_reviews.admin_module.mass_actions.ApproveProductReviewMassAction",
        "shuup_product_reviews.admin_module.mass_actions.RejectProductReviewMassAction"
    ]

    def get_queryset(self):
        return ProductReview.objects.filter(shop=get_shop(self.request))


class VendorReviewListView(BaseProductReviewListView):
    url_identifier = "vendor_reviews"

    mass_actions = [
        "shuup_product_reviews.admin_module.mass_actions.ApproveVendorReviewMassAction",
        "shuup_product_reviews.admin_module.mass_actions.RejectVendorReviewMassAction"
    ]

    def get_queryset(self):
        if djangoenv.has_installed("shuup_multivendor"):
            from shuup_multivendor.supplier_provider import get_supplier
            supplier = get_supplier(self.request)
            return ProductReview.objects.filter(order_line__supplier=supplier, shop=get_shop(self.request))
        return ProductReview.objects.none()
