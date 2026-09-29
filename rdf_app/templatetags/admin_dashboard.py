# # from django import template
# # from django.db.models import Sum
# # from django.utils import timezone

# # from ..models import (
# #     User,
# #     Product,
# #     Order,
# # )



# from django import template
# from django.db import models
# from django.db.models import Sum
# from django.utils import timezone

# from ..models import (
#     User,
#     Product,
#     Order,
# )

# register = template.Library()


# @register.simple_tag
# def dashboard_stats():
#     """
#     Returns all statistics required for the RDF admin dashboard.
#     """

#     today = timezone.localdate()

#     total_orders = Order.objects.count()

#     today_orders = Order.objects.filter(
#         created_at__date=today
#     ).count()

#     total_customers = User.objects.filter(
#         is_staff=False
#     ).count()

#     total_products = Product.objects.filter(
#         is_active=True
#     ).count()

#     pending_orders = Order.objects.filter(
#         status="pending"
#     ).count()

#     processing_orders = Order.objects.filter(
#         status="processing"
#     ).count()

#     delivered_orders = Order.objects.filter(
#         status="delivered"
#     ).count()

#     low_stock_products = Product.objects.filter(
#         is_active=True,
#         stock_quantity__gt=0,
#         stock_quantity__lte=models.F("low_stock_threshold"),
#     ).count()

#     out_of_stock_products = Product.objects.filter(
#         is_active=True,
#         stock_quantity__lte=0,
#     ).count()

#     total_sales = (
#         Order.objects
#         .exclude(status="cancelled")
#         .aggregate(
#             total=Sum("total_amount")
#         )
#         .get("total")
#         or 0
#     )

#     today_sales = (
#         Order.objects
#         .filter(
#             created_at__date=today
#         )
#         .exclude(status="cancelled")
#         .aggregate(
#             total=Sum("total_amount")
#         )
#         .get("total")
#         or 0
#     )

#     return {
#         "total_orders": total_orders,
#         "today_orders": today_orders,
#         "total_customers": total_customers,
#         "total_products": total_products,

#         "pending_orders": pending_orders,
#         "processing_orders": processing_orders,
#         "delivered_orders": delivered_orders,

#         "low_stock_products": low_stock_products,
#         "out_of_stock_products": out_of_stock_products,

#         "total_sales": total_sales,
#         "today_sales": today_sales,
#     }




# @register.simple_tag
# def recent_orders(limit=8):

#     return (
#         Order.objects
#         .select_related("user")
#         .order_by("-created_at")[:limit]
#     )
    
    



# @register.simple_tag
# def low_stock_products(limit=8):

#     return (
#         Product.objects
#         .filter(
#             is_active=True,
#             stock_quantity__gt=0,
#             stock_quantity__lte=models.F("low_stock_threshold"),
#         )
#         .select_related("category")
#         .order_by("stock_quantity")[:limit]
#     )
    
    
    
    


from datetime import timedelta

from django import template
from django.db import models
from django.db.models import Count, Sum, F
from django.utils import timezone

from ..models import (
    User,
    Product,
    Order,
    OrderItem,
)


register = template.Library()


# ============================================================
# DASHBOARD STATISTICS
# ============================================================

@register.simple_tag
def dashboard_stats():

    today = timezone.localdate()

    week_start = today - timedelta(days=6)

    month_start = today.replace(day=1)

    year_start = today.replace(
        month=1,
        day=1,
    )

    # --------------------------------------------------------
    # BASIC COUNTS
    # --------------------------------------------------------

    total_orders = Order.objects.count()

    today_orders = Order.objects.filter(
        created_at__date=today
    ).count()

    total_customers = User.objects.filter(
        is_staff=False
    ).count()

    total_products = Product.objects.filter(
        is_active=True
    ).count()

    # --------------------------------------------------------
    # ORDER STATUS
    # --------------------------------------------------------

    pending_orders = Order.objects.filter(
        status="pending"
    ).count()

    confirmed_orders = Order.objects.filter(
        status="confirmed"
    ).count()

    processing_orders = Order.objects.filter(
        status="processing"
    ).count()

    shipped_orders = Order.objects.filter(
        status="shipped"
    ).count()

    out_for_delivery_orders = Order.objects.filter(
        status="out_for_delivery"
    ).count()

    delivered_orders = Order.objects.filter(
        status="delivered"
    ).count()

    # --------------------------------------------------------
    # INVENTORY
    # --------------------------------------------------------

    low_stock_products = Product.objects.filter(
        is_active=True,
        stock_quantity__gt=0,
        stock_quantity__lte=F("low_stock_threshold"),
    ).count()

    out_of_stock_products = Product.objects.filter(
        is_active=True,
        stock_quantity__lte=0,
    ).count()

    # --------------------------------------------------------
    # SALES
    # --------------------------------------------------------

    valid_orders = Order.objects.exclude(
        status="cancelled"
    )

    total_sales = (
        valid_orders
        .aggregate(
            total=Sum("total_amount")
        )
        .get("total")
        or 0
    )

    today_sales = (
        valid_orders
        .filter(
            created_at__date=today
        )
        .aggregate(
            total=Sum("total_amount")
        )
        .get("total")
        or 0
    )

    week_sales = (
        valid_orders
        .filter(
            created_at__date__gte=week_start
        )
        .aggregate(
            total=Sum("total_amount")
        )
        .get("total")
        or 0
    )

    month_sales = (
        valid_orders
        .filter(
            created_at__date__gte=month_start
        )
        .aggregate(
            total=Sum("total_amount")
        )
        .get("total")
        or 0
    )

    year_sales = (
        valid_orders
        .filter(
            created_at__date__gte=year_start
        )
        .aggregate(
            total=Sum("total_amount")
        )
        .get("total")
        or 0
    )

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return {
        "total_orders": total_orders,
        "today_orders": today_orders,

        "total_customers": total_customers,
        "total_products": total_products,

        "pending_orders": pending_orders,
        "confirmed_orders": confirmed_orders,
        "processing_orders": processing_orders,
        "shipped_orders": shipped_orders,
        "out_for_delivery_orders": out_for_delivery_orders,
        "delivered_orders": delivered_orders,

        "low_stock_products": low_stock_products,
        "out_of_stock_products": out_of_stock_products,

        "total_sales": total_sales,
        "today_sales": today_sales,
        "week_sales": week_sales,
        "month_sales": month_sales,
        "year_sales": year_sales,
    }


# ============================================================
# RECENT ORDERS
# ============================================================

@register.simple_tag
def recent_orders(limit=8):

    return (
        Order.objects
        .select_related("user")
        .order_by("-created_at")[:limit]
    )


# ============================================================
# LOW STOCK PRODUCTS
# ============================================================

@register.simple_tag
def low_stock_products(limit=8):

    return (
        Product.objects
        .filter(
            is_active=True,
            stock_quantity__gt=0,
            stock_quantity__lte=F("low_stock_threshold"),
        )
        .select_related("category")
        .order_by("stock_quantity")[:limit]
    )


# ============================================================
# OUT OF STOCK PRODUCTS
# ============================================================

@register.simple_tag
def out_of_stock_products(limit=8):

    return (
        Product.objects
        .filter(
            is_active=True,
            stock_quantity__lte=0,
        )
        .select_related("category")
        .order_by("name")[:limit]
    )


# ============================================================
# BEST SELLING PRODUCTS
# ============================================================

@register.simple_tag
def best_selling_products(limit=10):

    return (
        OrderItem.objects
        .exclude(
            order__status="cancelled"
        )
        .values(
            "product",
            "product_name",
            "sku",
            "unit",
        )
        .annotate(
            total_quantity=Sum("quantity"),
            total_revenue=Sum("total_price"),
        )
        .order_by("-total_quantity")[:limit]
    )


# ============================================================
# ORDER STATUS ANALYTICS
# ============================================================

@register.simple_tag
def order_status_summary():

    statuses = (
        "pending",
        "confirmed",
        "processing",
        "shipped",
        "out_for_delivery",
        "delivered",
    )

    result = []

    for status in statuses:

        count = Order.objects.filter(
            status=status
        ).count()

        result.append(
            {
                "status": status,
                "label": dict(
                    Order.STATUS_CHOICES
                ).get(status, status),
                "count": count,
            }
        )

    return result


# ============================================================
# CUSTOMER ANALYTICS
# ============================================================

@register.simple_tag
def customer_stats():

    total_customers = User.objects.filter(
        is_staff=False
    ).count()

    customers_with_orders = (
        Order.objects
        .values("user")
        .distinct()
        .count()
    )

    return {
        "total_customers": total_customers,
        "customers_with_orders": customers_with_orders,
    }