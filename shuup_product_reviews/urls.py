# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from shuup_product_reviews.views import (
    ProductReviewCommentsView, ProductReviewsView, SupplierReviewCommentsView
)

urlpatterns = [
    url(r"product_reviews/$", login_required(ProductReviewsView.as_view()), name="product_reviews"),
    url(r"product_reviews/(?P<pk>\d+)/comments/$", ProductReviewCommentsView.as_view(), name="product_review_comments"),
    url(
        r"supplier_reviews/(?P<pk>\d+)/comments/$",
        SupplierReviewCommentsView.as_view(),
        name="supplier_review_comments"
    )
]
