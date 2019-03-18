# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Case, Count, QuerySet, Sum, Value, When
from django.utils.translation import ugettext_lazy as _
from enumfields import Enum, EnumIntegerField


class ReviewStatus(Enum):
    PENDING = 1
    APPROVED = 2
    REJECTED = 3

    class Labels:
        PENDING = _("Pending")
        APPROVED = _("Approved")
        REJECTED = _("Rejected")


class ProductReviewQuerySet(QuerySet):
    def for_reviewer(self, shop, reviewer):
        return self.filter(shop=shop, reviewer=reviewer)

    def approved(self):
        return self.filter(status=ReviewStatus.APPROVED)


class ProductReview(models.Model):
    shop = models.ForeignKey("shuup.Shop", verbose_name=_("shop"), related_name="product_reviews")
    product = models.ForeignKey("shuup.Product", verbose_name=_("product"), related_name="product_reviews")
    reviewer = models.ForeignKey("shuup.Contact", verbose_name=_("reviewer"), related_name="product_reviews")
    order_line = models.ForeignKey(
        "shuup.OrderLine", verbose_name=_("order line"), related_name="product_reviews")
    rating = models.PositiveIntegerField(
        verbose_name=_("rating"),
        validators=[MaxValueValidator(5), MinValueValidator(1)]
    )
    comment = models.TextField(blank=True, null=True, verbose_name=_("comment"))
    would_recommend = models.BooleanField(
        default=False,
        verbose_name=_("Would recommend to a friend?"),
        help_text=_("Indicates whether you would recommend this product to a friend.")
    )
    status = EnumIntegerField(ReviewStatus, db_index=True, default=ReviewStatus.PENDING)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_on = models.DateTimeField(auto_now=True)

    objects = ProductReviewQuerySet.as_manager()

    def __str__(self):
        return _("Review for {product} by {reviewer_name}").format(
            product=self.product,
            reviewer_name=self.reviewer.name
        )

    def save(self, *args, **kwargs):
        super(ProductReview, self).save(*args, **kwargs)
        recalculate_aggregation_for_product(self.product)
        recalculate_aggregation_for_supplier(self.order_line.supplier)
        from shuup_product_reviews.utils import bump_star_rating_cache
        bump_star_rating_cache(self.pk)

    def approve(self):
        self.status = ReviewStatus.APPROVED
        self.save()

    def reject(self):
        self.status = ReviewStatus.REJECTED
        self.save()


class ProductReviewAggregation(models.Model):
    product = models.OneToOneField(
        "shuup.Product",
        verbose_name=_("product"),
        related_name="product_reviews_aggregation",
    )
    rating = models.DecimalField(max_digits=2, decimal_places=1, verbose_name=_("rating"), default=0)
    review_count = models.PositiveIntegerField(verbose_name=_("review count"), default=0)
    would_recommend = models.PositiveIntegerField(verbose_name=_("users would recommend"), default=0)


class SupplierReviewAggregation(models.Model):
    supplier = models.OneToOneField(
        "shuup.Supplier",
        verbose_name=_("supplier"),
        related_name="supplier_reviews_aggregation",
    )
    rating = models.DecimalField(max_digits=2, decimal_places=1, verbose_name=_("rating"), default=0)
    review_count = models.PositiveIntegerField(verbose_name=_("review count"), default=0)


def recalculate_aggregation_for_queryset(queryset):
    if not queryset.exists():
        # Make sure there is no aggregation since there is no approved reviews
        return

    return queryset.aggregate(
        count=Count("pk"),
        rating=Avg("rating"),
        would_recommend=Sum(
            Case(
                When(would_recommend=True, then=Value(1)),
                When(would_recommend=False, then=Value(0)),
                default=Value(0),
                output_field=models.PositiveIntegerField()
            )
        )
    )


def recalculate_aggregation_for_product(product):
    reviews_agg = recalculate_aggregation_for_queryset(
        ProductReview.objects.filter(product=product, status=ReviewStatus.APPROVED)
    )
    if not reviews_agg:
        aggregation = ProductReviewAggregation.objects.filter(product=product).first()
        if aggregation:
            aggregation.delete()
        return

    ProductReviewAggregation.objects.update_or_create(product=product, defaults=dict(
        review_count=reviews_agg["count"],
        rating=reviews_agg["rating"],
        would_recommend=reviews_agg["would_recommend"]
    ))


def recalculate_aggregation_for_supplier(supplier):
    if not supplier:
        return

    reviews_agg = recalculate_aggregation_for_queryset(
        ProductReview.objects.filter(order_line__supplier=supplier, status=ReviewStatus.APPROVED)
    )
    if not reviews_agg:
        aggregation = SupplierReviewAggregation.objects.filter(supplier=supplier).first()
        if aggregation:
            aggregation.delete()
        return

    SupplierReviewAggregation.objects.update_or_create(supplier=supplier, defaults=dict(
        review_count=reviews_agg["count"],
        rating=reviews_agg["rating"]
    ))
