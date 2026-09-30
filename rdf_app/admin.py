




from decimal import Decimal

from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils import timezone



from datetime import datetime

from django.contrib import admin, messages
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils import timezone

from .models import (
    MilkSubscription,
    MilkSubscriptionItem,
    MilkDelivery,
    MilkBill,
)


from django.contrib import admin
from django.db.models import F, Count, Q
from django.utils.html import format_html

from .models import (
    Subscriber,
    User,
    UserProfile,
    Category,
    Product,
    Address,
    Cart,
    CartItem,
    Order,
    OrderItem,
)


class StockStatusFilter(admin.SimpleListFilter):

    title = "Stock Status"
    parameter_name = "stock_status"

    def lookups(self, request, model_admin):
        return (
            ("in_stock", "In Stock"),
            ("low_stock", "Low Stock"),
            ("out_of_stock", "Out of Stock"),
        )

    def queryset(self, request, queryset):

        if self.value() == "in_stock":
            return queryset.filter(
                stock_quantity__gt=0,
                is_in_stock=True,
            )

        if self.value() == "low_stock":
            return queryset.filter(
                stock_quantity__gt=0,
                stock_quantity__lte=F("low_stock_threshold"),
            )

        if self.value() == "out_of_stock":
            return queryset.filter(
                stock_quantity__lte=0,
            )

        return queryset

# ============================================================
# COMMON ADMIN SETTINGS
# ============================================================


admin.site.empty_value_display = "—"

admin.site.enable_nav_sidebar = True

admin.site.site_header = "Rajanna Dairy Farm"
admin.site.site_title = "RDF Admin"
admin.site.index_title = "Administration Dashboard"
admin.site.site_url = "/"


# ============================================================
# USER ADMIN
# ============================================================

@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        "user_id",
        "image_preview",
        "full_name",
        "email",
        "phone",
        "is_active",
        "is_staff",
        "date_joined",
    )

    list_display_links = (
        "user_id",
        "full_name",
        "email",
    )

    search_fields = (
        "user_id",
        "full_name",
        "email",
        "phone",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "date_joined",
    )

    readonly_fields = (
        "user_id",
        "image_preview",
        "date_joined",
        "last_login",
    )

    fieldsets = (
        (
            "Account Information",
            {
                "fields": (
                    "user_id",
                    "full_name",
                    "email",
                    "phone",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "address",
                    "image",
                    "image_preview",
                )
            },
        ),
        (
            "Account Status",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                )
            },
        ),
        (
            "Security",
            {
                "fields": (
                    "last_login",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "date_joined",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    ordering = ("-date_joined",)

    list_per_page = 25

    list_select_related = ()

    actions = (
        "activate_users",
        "deactivate_users",
    )

    # @admin.display(description="Photo")
    # def image_preview(self, obj):
    #     if obj.image:
    #         return format_html(
    #             '<img src="{}" width="45" height="45" '
    #             'style="object-fit:cover;border-radius:50%;" />',
    #             obj.image.url,
    #         )

    #     return "—"
    
    @admin.display(description="Image")
    def image_preview(self, obj):

        if not obj.image:
            return format_html(
                '<div class="rdf-image-placeholder">'
                '<i class="ph-bold ph-image"></i>'
                '</div>'
            )

        return format_html(
            '''
            <img
                src="{}"
                class="rdf-admin-thumb"
                alt="{}"
            />
            ''',
            obj.image.url,
            obj.full_name
        )

    @admin.action(description="Activate selected users")
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Deactivate selected users")
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)


# ============================================================
# USER PROFILE ADMIN
# ============================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "city",
        "state",
        "pincode",
        "gender",
        "completion",
        "updated_at",
    )

    list_display_links = (
        "user",
    )

    search_fields = (
        "user__full_name",
        "user__email",
        "user__phone",
        "city",
        "state",
        "pincode",
    )

    list_filter = (
        "gender",
        "state",
        "created_at",
        "updated_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "completion",
    )

    autocomplete_fields = (
        "user",
    )

    fieldsets = (
        (
            "User",
            {
                "fields": (
                    "user",
                )
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "date_of_birth",
                    "gender",
                    "bio",
                )
            },
        ),
        (
            "Location",
            {
                "fields": (
                    "city",
                    "state",
                    "pincode",
                )
            },
        ),
        (
            "Additional Contact",
            {
                "fields": (
                    "alternate_phone",
                )
            },
        ),
        (
            "Profile Completion",
            {
                "fields": (
                    "completion",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    ordering = ("-updated_at",)

    list_per_page = 25

    list_select_related = (
        "user",
    )

    @admin.display(description="Completion")
    def completion(self, obj):
        return f"{obj.completion_percentage()}%"


# ============================================================
# CATEGORY ADMIN
# ============================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "image_preview",
        "name",
        "product_count",
        "is_active",
        "is_featured",
        "created_at",
        "updated_at",
    )

    list_display_links = (
        "name",
    )

    search_fields = (
        "name",
        "slug",
        "description",
        "seo_title",
        "seo_description",
    )

    list_filter = (
        "is_active",
        "is_featured",
        "created_at",
    )

    readonly_fields = (
        "image_preview",
        "product_count",
        "created_at",
        "updated_at",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    fieldsets = (
        (
            "Category Information",
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                    "image",
                    "image_preview",
                )
            },
        ),
        (
            "Category Status",
            {
                "fields": (
                    "is_active",
                    "is_featured",
                )
            },
        ),
        (
            "SEO",
            {
                "fields": (
                    "seo_title",
                    "seo_description",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Statistics",
            {
                "fields": (
                    "product_count",
                ),
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    ordering = (
        "name",
    )

    list_per_page = 25

    actions = (
        "activate_categories",
        "deactivate_categories",
        "feature_categories",
        "unfeature_categories",
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        return queryset.annotate(
            admin_product_count=Count(
                "products",
                filter=Q(products__is_active=True),
                distinct=True,
            )
        )

    # @admin.display(description="Image")
    # def image_preview(self, obj):
    #     if obj.image:
    #         return format_html(
    #             '<img src="{}" width="50" height="50" '
    #             'style="object-fit:cover;border-radius:8px;" />',
    #             obj.image.url,
    #         )

    #     return "—"
    
    
    @admin.display(description="Image")
    def image_preview(self, obj):

        if not obj.image:
            return format_html(
                '<div class="rdf-image-placeholder">'
                '<i class="ph-bold ph-image"></i>'
                '</div>'
            )

        return format_html(
            '''
            <img
                src="{}"
                class="rdf-admin-thumb"
                alt="{}"
            />
            ''',
            obj.image.url,
            obj.name
        )

    @admin.display(description="Products", ordering="admin_product_count")
    def product_count(self, obj):
        return obj.admin_product_count

    @admin.action(description="Activate selected categories")
    def activate_categories(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Deactivate selected categories")
    def deactivate_categories(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Mark selected categories as featured")
    def feature_categories(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description="Remove selected categories from featured")
    def unfeature_categories(self, request, queryset):
        queryset.update(is_featured=False)




# ============================================================
# PRODUCT ADMIN
# ============================================================




@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "image_preview",
        "product_id",
        "name",
        "category",
        "sku",
        "price",
        "discount_percentage",
        "selling_price",
        "unit",
        "stock_quantity",
        "stock_status",
        "is_active",
        "is_featured",
        "created_at",
    )

    list_display_links = (
        "product_id",
        "name",
    )

    search_fields = (
        "product_id",
        "name",
        "sku",
        "slug",
        "short_description",
        "description",
    )

    list_filter = (
        "category",
        "unit",
        "is_active",
        "is_in_stock",
        "is_featured",        
    StockStatusFilter,
        "created_at",
    )

    # readonly_fields = (
    #     "product_id",
    #     "sku",
    #     # "selling_price",
    #     "is_in_stock",
    #     "image_preview",
    #     "created_at",
    #     "updated_at",
    # )
    
    readonly_fields = (
    "product_id",
    "sku",
    "is_in_stock",
    "image_preview",
    "selling_price_display",
    "seo_title_preview",
    "seo_description_preview",
    "created_at",
    "updated_at",
)

    prepopulated_fields = {
        "slug": ("name",),
    }

    autocomplete_fields = (
        "category",
    )

    fieldsets = (
        (
            "Product Information",
            {
                "fields": (
                    "product_id",
                    "category",
                    "name",
                    "slug",
                    "sku",
                )
            },
        ),
        (
            "Product Description",
            {
                "fields": (
                    "short_description",
                    "description",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "price",
                    "discount_percentage",
                     "selling_price_display",
                    # "selling_price",
                )
            },
        ),
        (
            "Inventory",
            {
                "fields": (
                    "unit",
                    "stock_quantity",
                    "low_stock_threshold",
                    "is_in_stock",
                )
            },
        ),
        (
            "Product Image",
            {
                "fields": (
                    "main_image",
                    "image_preview",
                )
            },
        ),
        (
            "Product Status",
            {
                "fields": (
                    "is_active",
                    "is_featured",
                )
            },
        ),
        (
    "SEO",
    {
        "fields": (
            "seo_title_preview",
            "seo_description_preview",
        ),
        "classes": ("collapse",),
    },
),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 25

    list_select_related = (
        "category",
    )

    # actions = (
    #     "activate_products",
    #     "deactivate_products",
    #     "feature_products",
    #     "unfeature_products",
    # )
    
    actions = (
    "activate_products",
    "deactivate_products",
    "feature_products",
    "unfeature_products",
    "mark_out_of_stock",
)

    # @admin.display(description="Image")
    # def image_preview(self, obj):
    #     if obj.main_image:
    #         return format_html(
    #             '<img src="{}" width="50" height="50" '
    #             'style="object-fit:cover;border-radius:8px;" />',
    #             obj.main_image.url,
    #         )

    #     return "—"
    
    @admin.display(description="Image")
    def image_preview(self, obj):

        if not obj.main_image:
            return format_html(
                '<div class="rdf-image-placeholder">'
                '<i class="ph-bold ph-image"></i>'
                '</div>'
            )

        return format_html(
            '''
            <img
                src="{}"
                class="rdf-admin-thumb"
                alt="{}"
            />
            ''',
            obj.main_image.url,
            obj.name
        )

    
    @admin.display(description="SEO Title")
    def seo_title_preview(self, obj):
        return obj.seo_title or "—"


    @admin.display(description="SEO Description")
    def seo_description_preview(self, obj):
        return obj.seo_description or "—"


    # @admin.display(description="Selling Price")
    # def selling_price_display(self, obj):
    #     if obj.selling_price is not None:
    #         return f"₹{obj.selling_price}"
    #     return "—"
    
    @admin.display(description="Selling Price")
    def selling_price_display(self, obj):

        if obj.selling_price is None:
            return "—"

        return format_html(
            '<strong class="rdf-price">₹{}</strong>',
            obj.selling_price
        )


    @admin.display(description="Stock")
    def stock_status(self, obj):

        if not obj.is_active:
            return format_html(
                '<span class="rdf-badge rdf-badge-neutral">'
                'Inactive'
                '</span>'
            )

        if obj.stock_quantity <= 0:
            return format_html(
                '<span class="rdf-badge rdf-badge-danger">'
                'Out of Stock'
                '</span>'
            )

        if obj.stock_quantity <= obj.low_stock_threshold:
            return format_html(
                '<span class="rdf-badge rdf-badge-warning">'
                'Low Stock'
                '</span>'
            )

        return format_html(
            '<span class="rdf-badge rdf-badge-success">'
            'In Stock'
            '</span>'
        )
    
        
    @admin.display(description="Active")
    def active_badge(self, obj):

        if obj.is_active:
            return format_html(
                '<span class="rdf-badge rdf-badge-success">'
                'Active'
                '</span>'
            )

        return format_html(
            '<span class="rdf-badge rdf-badge-neutral">'
            'Inactive'
            '</span>'
        )


    @admin.display(description="Featured")
    def featured_badge(self, obj):

        if obj.is_featured:
            return format_html(
                '<span class="rdf-badge rdf-badge-purple">'
                'Featured'
                '</span>'
            )

        return "—"
    
    
    @admin.action(description="Activate selected products")
    def activate_products(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Deactivate selected products")
    def deactivate_products(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Mark selected products as featured")
    def feature_products(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description="Remove selected products from featured")
    def unfeature_products(self, request, queryset):
        queryset.update(is_featured=False)
        
    @admin.action(description="Mark selected products as Out of Stock")
    def mark_out_of_stock(self, request, queryset):
        queryset.update(
            stock_quantity=0,
            is_in_stock=False,
        )
        
        
    
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)

        # Only set a default category when creating a new product.
        if not request.resolver_match.kwargs.get("object_id"):
            first_category = (
                Category.objects
                .filter(is_active=True)
                .order_by("name")
                .first()
            )

            if first_category:
                initial["category"] = first_category.pk

        return initial
        
    def save_model(self, request, obj, form, change):

        # Save the product first.
        super().save_model(
            request,
            obj,
            form,
            change
        )

        # Only announce newly-created products.
        if change:
            return

        from django.urls import reverse
        from .utils import send_new_product_announcement

        try:

            product_path = reverse(
                "product-detail",
                args=[obj.product_id]
            )

            product_url = request.build_absolute_uri(
                product_path
            )

            print(
                "PRODUCT URL ==",
                product_url
            )

            result = send_new_product_announcement(
                product=obj,
                product_url=product_url
            )

            print(
                "PRODUCT ANNOUNCEMENT RESULT ==",
                result
            )

            if result["failed"] == 0:

                self.message_user(
                    request,
                    (
                        f"Product '{obj.name}' created successfully. "
                        f"Announcement sent to "
                        f"{result['sent']} recipient(s)."
                    ),
                    level=messages.SUCCESS
                )

            elif result["sent"] > 0:

                self.message_user(
                    request,
                    (
                        f"Product '{obj.name}' created successfully. "
                        f"Announcement: "
                        f"{result['sent']} sent, "
                        f"{result['failed']} failed."
                    ),
                    level=messages.WARNING
                )

            else:

                self.message_user(
                    request,
                    (
                        f"Product '{obj.name}' created successfully, "
                        f"but announcement emails could not be sent."
                    ),
                    level=messages.WARNING
                )

        except Exception as exc:

            print(
                "PRODUCT ANNOUNCEMENT ERROR ==",
                repr(exc)
            )

            # IMPORTANT:
            # Product has already been saved.
            # Never fail the admin request because email failed.
            self.message_user(
                request,
                (
                    f"Product '{obj.name}' was created successfully, "
                    f"but the announcement could not be sent."
                ),
                level=messages.WARNING
            )
    # def save_model(self, request, obj, form, change):

    #     super().save_model(
    #         request,
    #         obj,
    #         form,
    #         change
    #     )

    #     if not change:

    #         from django.urls import reverse
    #         from .utils import send_new_product_announcement

    #         try:

    #             product_path = reverse(
    #                 "product-detail",
    #                 args=[obj.product_id]
    #             )

    #             product_url = request.build_absolute_uri(
    #                 product_path
    #             )
    #             print("product url==",product_url)

    #             result = send_new_product_announcement(
    #                 product=obj,
    #                 product_url=product_url
    #             )

    #             if result["failed"] == 0:

    #                 self.message_user(
    #                     request,
    #                     (
    #                         f"Product '{obj.name}' created successfully. "
    #                         f"Announcement sent to "
    #                         f"{result['sent']} recipients."
    #                     ),
    #                     level=messages.SUCCESS
    #                 )

    #             else:

    #                 self.message_user(
    #                     request,
    #                     (
    #                         f"Product '{obj.name}' created successfully. "
    #                         f"Announcement: "
    #                         f"{result['sent']} sent, "
    #                         f"{result['failed']} failed."
    #                     ),
    #                     level=messages.WARNING
    #                 )

    #         except Exception as exc:

    #             self.message_user(
    #                 request,
    #                 (
    #                     f"Product '{obj.name}' was created, "
    #                     f"but the announcement could not be sent. "
    #                     f"Error: {exc}"
    #                 ),
    #                 level=messages.ERROR
    #             )


# ============================================================
# ORDER ITEM INLINE
# ============================================================

class OrderItemInline(admin.TabularInline):

    model = OrderItem

    extra = 0

    can_delete = False

    fields = (
        "product",
        "product_name",
        "sku",
        "unit",
        "quantity",
        "unit_price",
        "discount_percentage",
        "total_price",
    )

    readonly_fields = (
        "product",
        "product_name",
        "sku",
        "unit",
        "quantity",
        "unit_price",
        "discount_percentage",
        "total_price",
    )

    autocomplete_fields = (
        "product",
    )


# ============================================================
# ORDER ADMIN
# ============================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_number",
        "customer_name",
        "customer_phone",
        "total_amount",
        "payment_method",
        "payment_status",
        # "status",
        "status_badge",
        "created_at",
    )

    list_display_links = (
        "order_number",
    )

    search_fields = (
        "order_number",
        "full_name",
        "phone_number",
        "city",
        "pincode",
        "user__full_name",
        "user__email",
        "user__phone",
    )

    list_filter = (
        "status",
        "payment_method",
        "payment_status",
        "state",
        "city",
        "created_at",
    )

    date_hierarchy = "created_at"

    ordering = (
        "-created_at",
    )

    list_per_page = 25

    list_select_related = (
        "user",
    )

    readonly_fields = (
        "order_number",
        "user",
        "full_name",
        "phone_number",
        "address_line1",
        "address_line2",
        "landmark",
        "city",
        "state",
        "pincode",
        "subtotal",
        "delivery_charge",
        "total_amount",
        "payment_method",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Order Information",
            {
                "fields": (
                    "order_number",
                    "user",
                    "status",
                )
            },
        ),
        (
            "Customer Information",
            {
                "fields": (
                    "full_name",
                    "phone_number",
                )
            },
        ),
        (
            "Delivery Address",
            {
                "fields": (
                    "address_line1",
                    "address_line2",
                    "landmark",
                    "city",
                    "state",
                    "pincode",
                )
            },
        ),
        (
            "Payment",
            {
                "fields": (
                    "payment_method",
                    "payment_status",
                )
            },
        ),
        (
            "Order Amount",
            {
                "fields": (
                    "subtotal",
                    "delivery_charge",
                    "total_amount",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = (
        OrderItemInline,
    )

    actions = (
        "mark_confirmed",
        "mark_processing",
        "mark_shipped",
        "mark_out_for_delivery",
        "mark_delivered",
    )
    
    
    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):

        status = obj.status

        mapping = {
            "pending": (
                "rdf-badge-warning",
                "Pending",
            ),
            "confirmed": (
                "rdf-badge-info",
                "Confirmed",
            ),
            "processing": (
                "rdf-badge-purple",
                "Processing",
            ),
            "shipped": (
                "rdf-badge-blue",
                "Shipped",
            ),
            "out_for_delivery": (
                "rdf-badge-blue",
                "Out for Delivery",
            ),
            "delivered": (
                "rdf-badge-success",
                "Delivered",
            ),
            "cancelled": (
                "rdf-badge-danger",
                "Cancelled",
            ),
        }

        css_class, label = mapping.get(
            status,
            ("rdf-badge-neutral", obj.get_status_display())
        )

        return format_html(
            '<span class="rdf-badge {}">{}</span>',
            css_class,
            label
        )

    @admin.display(description="Customer", ordering="full_name")
    def customer_name(self, obj):
        return obj.full_name

    @admin.display(description="Phone")
    def customer_phone(self, obj):
        return obj.phone_number

    @admin.action(description="Mark selected orders as Confirmed")
    def mark_confirmed(self, request, queryset):
        queryset.update(status="confirmed")

    @admin.action(description="Mark selected orders as Processing")
    def mark_processing(self, request, queryset):
        queryset.update(status="processing")

    @admin.action(description="Mark selected orders as Shipped")
    def mark_shipped(self, request, queryset):
        queryset.update(status="shipped")

    @admin.action(description="Mark selected orders as Out for Delivery")
    def mark_out_for_delivery(self, request, queryset):
        queryset.update(status="out_for_delivery")

    @admin.action(description="Mark selected orders as Delivered")
    def mark_delivered(self, request, queryset):
        queryset.update(
            status="delivered",
            payment_status="paid",
        )


# ============================================================
# ADDRESS ADMIN
# ============================================================

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):

    list_display = (
        "full_name",
        "phone_number",
        "city",
        "state",
        "pincode",
        "address_type",
        "is_default",
        "created_at",
    )

    search_fields = (
        "full_name",
        "phone_number",
        "city",
        "state",
        "pincode",
        "address_line1",
        "address_line2",
        "landmark",
        "user__full_name",
        "user__email",
        "user__phone",
    )

    list_filter = (
        "address_type",
        "is_default",
        "state",
        "city",
        "created_at",
    )

    autocomplete_fields = (
        "user",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Customer",
            {
                "fields": (
                    "user",
                )
            },
        ),
        (
            "Address Information",
            {
                "fields": (
                    "full_name",
                    "phone_number",
                    "address_line1",
                    "address_line2",
                    "landmark",
                    "city",
                    "state",
                    "pincode",
                )
            },
        ),
        (
            "Address Settings",
            {
                "fields": (
                    "address_type",
                    "is_default",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 25


# ============================================================
# CART ITEM INLINE
# ============================================================

class CartItemInline(admin.TabularInline):

    model = CartItem

    extra = 0

    fields = (
        "product",
        "quantity",
        "added_at",
        "updated_at",
    )

    readonly_fields = (
        "product",
        "quantity",
        "added_at",
        "updated_at",
    )

    can_delete = False


# ============================================================
# CART ADMIN
# ============================================================

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "total_items_display",
        "subtotal_display",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__full_name",
        "user__email",
        "user__phone",
        "user__user_id",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "total_items_display",
        "subtotal_display",
    )

    autocomplete_fields = (
        "user",
    )

    inlines = (
        CartItemInline,
    )

    ordering = (
        "-updated_at",
    )

    list_per_page = 25

    @admin.display(description="Items")
    def total_items_display(self, obj):
        return obj.total_items

    @admin.display(description="Subtotal")
    def subtotal_display(self, obj):
        return f"₹{obj.subtotal}"


# ============================================================
# CART ITEM ADMIN
# ============================================================

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = (
        "cart",
        "product",
        "quantity",
        "item_total_display",
        "added_at",
        "updated_at",
    )

    search_fields = (
        "cart__user__full_name",
        "cart__user__email",
        "cart__user__phone",
        "product__name",
        "product__product_id",
        "product__sku",
    )

    list_filter = (
        "added_at",
        "updated_at",
    )

    autocomplete_fields = (
        "cart",
        "product",
    )

    readonly_fields = (
        "added_at",
        "updated_at",
        "item_total_display",
    )

    ordering = (
        "-updated_at",
    )

    list_per_page = 25

    @admin.display(description="Item Total")
    def item_total_display(self, obj):
        return f"₹{obj.item_total}"
    
    



@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):

    list_display = (
        "email",
        "created_at",
    )

    list_display_links = (
        "email",
    )

    search_fields = (
        "email",
    )

    list_filter = (
        "created_at",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 25

    date_hierarchy = "created_at"
    
    






from .models import (
    User,
    UserProfile,
    Category,
    Product,
    Address,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Subscriber,
    MilkSubscription,
    MilkSubscriptionItem,
    MilkDelivery,
    MilkBill,
)



# @admin.register(MilkDelivery)
# class MilkDeliveryAdmin(admin.ModelAdmin):
#     list_display = (
#         "delivery_date",
#         "customer_name",
#         "product_name",
#         "quantity",
#         "total_amount",
#         "status",
#         "delivered_at",
#     )

#     list_display_links = ("delivery_date",)

#     search_fields = (
#         "subscription__subscription_number",
#         "subscription__user__email",
#         "subscription__user__first_name",
#         "subscription__user__last_name",
#         "subscription_item__product__name",
#     )

#     list_filter = (
#         "status",
#         "delivery_date",
#     )

#     autocomplete_fields = (
#         "subscription",
#         "subscription_item",
#     )

#     readonly_fields = (
#         "created_at",
#         "updated_at",
#     )

#     fieldsets = (
#         (
#             "Delivery Information",
#             {
#                 "fields": (
#                     "subscription",
#                     "subscription_item",
#                     "delivery_date",
#                 )
#             },
#         ),
#         (
#             "Milk Details",
#             {
#                 "fields": (
#                     "quantity",
#                     "unit_price",
#                     "total_amount",
#                 )
#             },
#         ),
#         (
#             "Delivery Status",
#             {
#                 "fields": (
#                     "status",
#                     "delivered_at",
#                     "notes",
#                 )
#             },
#         ),
#         (
#             "System Information",
#             {
#                 "fields": (
#                     "created_at",
#                     "updated_at",
#                 ),
#                 "classes": ("collapse",),
#             },
#         ),
#     )

#     ordering = (
#         "-delivery_date",
#         "-created_at",
#     )

#     list_per_page = 50

#     date_hierarchy = "delivery_date"

#     list_select_related = (
#         "subscription",
#         "subscription__user",
#         "subscription_item",
#         "subscription_item__product",
#     )

#     @admin.display(description="Customer")
#     def customer_name(self, obj):
#         user = obj.subscription.user

#         if hasattr(user, "get_full_name"):
#             name = user.get_full_name()

#             if name:
#                 return name

#         return user.email

#     @admin.display(description="Product")
#     def product_name(self, obj):
#         return obj.subscription_item.product.name




@admin.register(MilkDelivery)
class MilkDeliveryAdmin(admin.ModelAdmin):

    list_display = (
        "delivery_date",
        "customer_name",
        "product_name",
        "quantity",
        "total_amount",
        "status",
        "delivered_at",
    )

    list_display_links = (
        "delivery_date",
    )

    search_fields = (
        "subscription__subscription_number",
        "subscription__user__email",
        "subscription__user__full_name",
        "subscription__user__phone",
        "subscription_item__product__name",
        "subscription__address__full_name",
        "subscription__address__phone_number",
    )

    list_filter = (
        "status",
        "delivery_date",
    )

    autocomplete_fields = (
        "subscription",
        "subscription_item",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Delivery Information",
            {
                "fields": (
                    "subscription",
                    "subscription_item",
                    "delivery_date",
                )
            },
        ),

        (
            "Milk Details",
            {
                "fields": (
                    "quantity",
                    "unit_price",
                    "total_amount",
                )
            },
        ),

        (
            "Delivery Status",
            {
                "fields": (
                    "status",
                    "delivered_at",
                    "notes",
                )
            },
        ),

        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    ordering = (
        "-delivery_date",
        "-created_at",
    )

    list_per_page = 50

    date_hierarchy = "delivery_date"

    list_select_related = (
        "subscription",
        "subscription__user",
        "subscription__address",
        "subscription_item",
        "subscription_item__product",
    )

    # ==================================================
    # CUSTOM ADMIN URLS
    # ==================================================

    def get_urls(self):

        urls = super().get_urls()

        custom_urls = [
            path(
                "milk-operations/",
                self.admin_site.admin_view(
                    self.milk_operations_dashboard
                ),
                name="milk-operations-dashboard",
            ),

            path(
                "milk-operations/delivery/<int:delivery_id>/delivered/",
                self.admin_site.admin_view(
                    self.mark_delivery_delivered
                ),
                name="milk-delivery-mark-delivered",
            ),

            path(
                "milk-operations/delivery/<int:delivery_id>/missed/",
                self.admin_site.admin_view(
                    self.mark_delivery_missed
                ),
                name="milk-delivery-mark-missed",
            ),
        ]

        return custom_urls + urls

    # ==================================================
    # MILK OPERATIONS DASHBOARD
    # ==================================================

    def milk_operations_dashboard(self, request):

        today = timezone.localdate()

        # ----------------------------------------------
        # SUBSCRIPTIONS
        # ----------------------------------------------

        active_subscriptions = (
            MilkSubscription.objects
            .filter(status="active")
            .count()
        )

        pending_subscriptions = (
            MilkSubscription.objects
            .filter(status="pending")
            .count()
        )

        paused_subscriptions = (
            MilkSubscription.objects
            .filter(status="paused")
            .count()
        )

        cancelled_subscriptions = (
            MilkSubscription.objects
            .filter(status="cancelled")
            .count()
        )

        # ----------------------------------------------
        # TODAY'S DELIVERIES
        # ----------------------------------------------

        todays_deliveries = (
            MilkDelivery.objects
            .filter(delivery_date=today)
            .select_related(
                "subscription",
                "subscription__user",
                "subscription__address",
                "subscription_item",
                "subscription_item__product",
            )
            .order_by(
                "status",
                "subscription__user__full_name",
            )
        )

        total_deliveries = todays_deliveries.count()

        scheduled_deliveries = (
            todays_deliveries
            .filter(status="scheduled")
            .count()
        )

        delivered_deliveries = (
            todays_deliveries
            .filter(status="delivered")
            .count()
        )

        missed_deliveries = (
            todays_deliveries
            .filter(status="missed")
            .count()
        )

        skipped_deliveries = (
            todays_deliveries
            .filter(status="skipped")
            .count()
        )

        # ----------------------------------------------
        # TODAY'S MILK QUANTITY
        # ----------------------------------------------

        today_quantity = (
            todays_deliveries
            .aggregate(
                total=Sum("quantity")
            )
            .get("total")
            or 0
        )

        # ----------------------------------------------
        # TODAY'S DELIVERY VALUE
        # ----------------------------------------------

        today_delivery_value = (
            todays_deliveries
            .aggregate(
                total=Sum("total_amount")
            )
            .get("total")
            or 0
        )

        # ----------------------------------------------
        # CURRENT MONTH BILLING
        # ----------------------------------------------

        current_month = today.month
        current_year = today.year

        current_bills = MilkBill.objects.filter(
            billing_month=current_month,
            billing_year=current_year,
        )

        total_billed = (
            current_bills
            .aggregate(
                total=Sum("total_amount")
            )
            .get("total")
            or 0
        )

        total_collected = (
            current_bills
            .aggregate(
                total=Sum("paid_amount")
            )
            .get("total")
            or 0
        )

        total_pending = (
            current_bills
            .aggregate(
                total=Sum("pending_amount")
            )
            .get("total")
            or 0
        )

        pending_bills = (
            current_bills
            .filter(
                pending_amount__gt=0
            )
            .count()
        )

        context = {
            **self.admin_site.each_context(request),

            "title": "Milk Operations",

            "today": today,

            # Subscription statistics
            "active_subscriptions": active_subscriptions,
            "pending_subscriptions": pending_subscriptions,
            "paused_subscriptions": paused_subscriptions,
            "cancelled_subscriptions": cancelled_subscriptions,

            # Delivery statistics
            "total_deliveries": total_deliveries,
            "scheduled_deliveries": scheduled_deliveries,
            "delivered_deliveries": delivered_deliveries,
            "missed_deliveries": missed_deliveries,
            "skipped_deliveries": skipped_deliveries,

            # Quantity/value
            "today_quantity": today_quantity,
            "today_delivery_value": today_delivery_value,

            # Billing
            "total_billed": total_billed,
            "total_collected": total_collected,
            "total_pending": total_pending,
            "pending_bills": pending_bills,

            # Deliveries
            "todays_deliveries": todays_deliveries,

            # URLs
            "milk_delivery_url": reverse(
                "admin:rdf_app_milkdelivery_changelist"
            ),

            "milk_subscription_url": reverse(
                "admin:rdf_app_milksubscription_changelist"
            ),

            "milk_bill_url": reverse(
                "admin:rdf_app_milkbill_changelist"
            ),
        }

        return render(
            request,
            "admin/rdf_app/milk_operations.html",
            context,
        )

    # ==================================================
    # MARK DELIVERY DELIVERED
    # ==================================================

    def mark_delivery_delivered(
        self,
        request,
        delivery_id,
    ):

        if request.method != "POST":
            return redirect(
                "admin:milk-operations-dashboard"
            )

        delivery = (
            MilkDelivery.objects
            .filter(id=delivery_id)
            .first()
        )

        if not delivery:

            self.message_user(
                request,
                "Delivery not found.",
                level=messages.ERROR,
            )

            return redirect(
                "admin:milk-operations-dashboard"
            )

        if delivery.status == "delivered":

            self.message_user(
                request,
                "This delivery is already marked as delivered.",
                level=messages.WARNING,
            )

            return redirect(
                "admin:milk-operations-dashboard"
            )

        delivery.status = "delivered"
        delivery.delivered_at = timezone.now()

        delivery.save(
            update_fields=[
                "status",
                "delivered_at",
                "updated_at",
            ]
        )

        self.message_user(
            request,
            (
                f"Delivery for "
                f"{delivery.subscription.user.email} "
                f"marked as delivered."
            ),
            level=messages.SUCCESS,
        )

        return redirect(
            "admin:milk-operations-dashboard"
        )

    # ==================================================
    # MARK DELIVERY MISSED
    # ==================================================

    def mark_delivery_missed(
        self,
        request,
        delivery_id,
    ):

        if request.method != "POST":
            return redirect(
                "admin:milk-operations-dashboard"
            )

        delivery = (
            MilkDelivery.objects
            .filter(id=delivery_id)
            .first()
        )

        if not delivery:

            self.message_user(
                request,
                "Delivery not found.",
                level=messages.ERROR,
            )

            return redirect(
                "admin:milk-operations-dashboard"
            )

        if delivery.status == "delivered":

            self.message_user(
                request,
                "A delivered delivery cannot be marked as missed.",
                level=messages.ERROR,
            )

            return redirect(
                "admin:milk-operations-dashboard"
            )

        delivery.status = "missed"
        delivery.delivered_at = None

        delivery.save(
            update_fields=[
                "status",
                "delivered_at",
                "updated_at",
            ]
        )

        self.message_user(
            request,
            (
                f"Delivery for "
                f"{delivery.subscription.user.email} "
                f"marked as missed."
            ),
            level=messages.WARNING,
        )

        return redirect(
            "admin:milk-operations-dashboard"
        )

    # ==================================================
    # DISPLAY HELPERS
    # ==================================================

    @admin.display(description="Customer")
    def customer_name(self, obj):

        user = obj.subscription.user

        if hasattr(user, "get_full_name"):

            name = user.get_full_name()

            if name:
                return name

        return user.email

    @admin.display(description="Product")
    def product_name(self, obj):

        return obj.subscription_item.product.name





class MilkSubscriptionItemInline(admin.TabularInline):
    model = MilkSubscriptionItem
    extra = 1

    fields = (
        "product",
        "quantity",
        "price_per_unit",
        "frequency",
        "start_date",
        "end_date",
    )

    autocomplete_fields = (
        "product",
    )

    readonly_fields = ()

    show_change_link = True




# @admin.register(MilkSubscription)
# class MilkSubscriptionAdmin(admin.ModelAdmin):

#     list_display = (
#         "subscription_number",
#         "customer_name",
#         "address",
#         "start_date",
#         "status",
#         "billing_cycle",
#         "created_at",
#     )

#     list_display_links = (
#         "subscription_number",
#     )

#     search_fields = (
#         "subscription_number",
#         "user__email",
#         "user__full_name",
#         "user__phone",
#         "address__full_name",
#         "address__phone_number",
#         "address__city",
#     )

#     list_filter = (
#         "status",
#         "billing_cycle",
#         "start_date",
#         "created_at",
#     )

#     readonly_fields = (
#         "subscription_number",
#         "created_at",
#         "updated_at",
#     )

#     autocomplete_fields = (
#         "user",
#         "address",
#     )

#     fieldsets = (
#         (
#             "Subscription Information",
#             {
#                 "fields": (
#                     "subscription_number",
#                     "user",
#                     "address",
#                 )
#             },
#         ),
#         (
#             "Subscription Period",
#             {
#                 "fields": (
#                     "start_date",
#                     "end_date",
#                     "billing_cycle",
#                     "status",
#                 )
#             },
#         ),
#         (
#             "Notes",
#             {
#                 "fields": (
#                     "notes",
#                 )
#             },
#         ),
#         (
#             "System Information",
#             {
#                 "fields": (
#                     "created_at",
#                     "updated_at",
#                 ),
#                 "classes": ("collapse",),
#             },
#         ),
#     )

#     inlines = (
#         MilkSubscriptionItemInline,
#     )

#     ordering = (
#         "-created_at",
#     )

#     list_per_page = 25

#     date_hierarchy = "start_date"

#     list_select_related = (
#         "user",
#         "address",
#     )

#     @admin.display(
#         description="Customer",
#         ordering="user__full_name",
#     )
#     def customer_name(self, obj):
#         if hasattr(obj.user, "get_full_name"):
#             name = obj.user.get_full_name()

#             if name:
#                 return name

#         return obj.user.email
    






@admin.register(MilkSubscription)
class MilkSubscriptionAdmin(admin.ModelAdmin):

    list_display = (
        "subscription_number",
        "customer_name",
        "address",
        "start_date",
        "status",
        "billing_cycle",
        "created_at",
    )

    list_display_links = (
        "subscription_number",
    )

    search_fields = (
        "subscription_number",
        "user__email",
        "user__full_name",
        "user__phone",
        "address__full_name",
        "address__phone_number",
        "address__city",
    )

    list_filter = (
        "status",
        "billing_cycle",
        "start_date",
        "created_at",
    )

    readonly_fields = (
        "subscription_number",
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "user",
        "address",
    )

    fieldsets = (
        (
            "Subscription Information",
            {
                "fields": (
                    "subscription_number",
                    "user",
                    "address",
                )
            },
        ),

        (
            "Subscription Period",
            {
                "fields": (
                    "start_date",
                    "end_date",
                    "billing_cycle",
                    "status",
                )
            },
        ),

        (
            "Notes",
            {
                "fields": (
                    "notes",
                )
            },
        ),

        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = (
        MilkSubscriptionItemInline,
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 25

    date_hierarchy = "start_date"

    list_select_related = (
        "user",
        "address",
    )

    actions = (
        "approve_subscriptions",
        "pause_subscriptions",
        "activate_subscriptions",
        "cancel_subscriptions",
    )

    # ==================================================
    # ADMIN ACTIONS
    # ==================================================

    @admin.action(description="Approve selected subscriptions")
    def approve_subscriptions(self, request, queryset):

        updated_count = 0
        skipped_count = 0

        for subscription in queryset:

            if subscription.status != "pending":
                skipped_count += 1
                continue

            subscription.status = "active"

            subscription.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            updated_count += 1

        if updated_count:
            self.message_user(
                request,
                (
                    f"{updated_count} subscription(s) "
                    f"approved and activated."
                ),
                level=messages.SUCCESS,
            )

        if skipped_count:
            self.message_user(
                request,
                (
                    f"{skipped_count} subscription(s) "
                    f"were skipped because they were not pending."
                ),
                level=messages.WARNING,
            )

    @admin.action(description="Pause selected subscriptions")
    def pause_subscriptions(self, request, queryset):

        updated_count = 0
        skipped_count = 0

        for subscription in queryset:

            if subscription.status != "active":
                skipped_count += 1
                continue

            subscription.status = "paused"

            subscription.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            updated_count += 1

        if updated_count:
            self.message_user(
                request,
                (
                    f"{updated_count} subscription(s) "
                    f"paused successfully."
                ),
                level=messages.SUCCESS,
            )

        if skipped_count:
            self.message_user(
                request,
                (
                    f"{skipped_count} subscription(s) "
                    f"were skipped because they were not active."
                ),
                level=messages.WARNING,
            )

    @admin.action(description="Activate selected subscriptions")
    def activate_subscriptions(self, request, queryset):

        updated_count = 0
        skipped_count = 0

        for subscription in queryset:

            if subscription.status != "paused":
                skipped_count += 1
                continue

            subscription.status = "active"

            subscription.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            updated_count += 1

        if updated_count:
            self.message_user(
                request,
                (
                    f"{updated_count} subscription(s) "
                    f"activated successfully."
                ),
                level=messages.SUCCESS,
            )

        if skipped_count:
            self.message_user(
                request,
                (
                    f"{skipped_count} subscription(s) "
                    f"were skipped because they were not paused."
                ),
                level=messages.WARNING,
            )

    @admin.action(description="Cancel selected subscriptions")
    def cancel_subscriptions(self, request, queryset):

        updated_count = 0
        skipped_count = 0

        for subscription in queryset:

            if subscription.status not in (
                "pending",
                "active",
                "paused",
            ):
                skipped_count += 1
                continue

            subscription.status = "cancelled"

            subscription.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            updated_count += 1

        if updated_count:
            self.message_user(
                request,
                (
                    f"{updated_count} subscription(s) "
                    f"cancelled successfully."
                ),
                level=messages.SUCCESS,
            )

        if skipped_count:
            self.message_user(
                request,
                (
                    f"{skipped_count} subscription(s) "
                    f"were skipped because they were already "
                    f"cancelled or expired."
                ),
                level=messages.WARNING,
            )

    # ==================================================
    # CUSTOMER DISPLAY
    # ==================================================

    @admin.display(
        description="Customer",
        ordering="user__full_name",
    )
    def customer_name(self, obj):

        if obj.user.full_name:
            return obj.user.full_name

        return obj.user.email










@admin.register(MilkSubscriptionItem)
class MilkSubscriptionItemAdmin(admin.ModelAdmin):

    list_display = (
        "subscription",
        "product",
        "quantity",
        "price_per_unit",
        "frequency",
        "start_date",
        "end_date",
    )

    search_fields = (
        "subscription__subscription_number",
        "subscription__user__email",
        "subscription__user__full_name",
        "subscription__user__phone",
        "product__name",
        "product__sku",
    )

    list_filter = (
        "frequency",
        "start_date",
        "end_date",
    )

    autocomplete_fields = (
        "subscription",
        "product",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Subscription Item",
            {
                "fields": (
                    "subscription",
                    "product",
                    "quantity",
                    "price_per_unit",
                    "frequency",
                )
            },
        ),
        (
            "Period",
            {
                "fields": (
                    "start_date",
                    "end_date",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 25

    @admin.display(description="Daily Amount")
    def daily_amount_display(self, obj):
        return f"₹{obj.daily_amount}"




# @admin.register(MilkBill)
# class MilkBillAdmin(admin.ModelAdmin):

#     list_display = (
#         "billing_period",
#         "customer_name",
#         "total_amount",
#         "paid_amount",
#         "pending_amount",
#         "status",
#         "payment_date",       
#     "email_status",
#     )

#     list_display_links = (
#         "billing_period",
#     )

#     search_fields = (
#         "subscription__subscription_number",
#         "subscription__user__email",
#         "subscription__user__first_name",
#         "subscription__user__last_name",
#     )

#     list_filter = (
#         "status",
#         "billing_year",
#         "billing_month",
#         "payment_date",
#     )

#     autocomplete_fields = (
#         "subscription",
#     )

#     # readonly_fields = (
#     #     "pending_amount",
#     #     "created_at",
#     #     "updated_at",
#     # )
    
#     readonly_fields = (
#     "pending_amount",
#     "email_sent",
#     "email_sent_at",
#     "created_at",
#     "updated_at",
# )

#     fieldsets = (
#         (
#             "Bill Information",
#             {
#                 "fields": (
#                     "subscription",
#                     "billing_month",
#                     "billing_year",
#                 )
#             },
#         ),
#         (
#             "Amount",
#             {
#                 "fields": (
#                     "total_amount",
#                     "paid_amount",
#                     "pending_amount",
#                 )
#             },
#         ),
#         (
#             "Cash Payment",
#             {
#                 "fields": (
#                     "status",
#                     "payment_date",
#                     "notes",
                    
#                 )
#             },
#         ),
#         (
#             "System Information",
#             {
#                 "fields": (
#                     "created_at",
#                     "updated_at",
#                 ),
#                 "classes": ("collapse",),
#             },
#         ),
#         (
#     "Email Information",
#     {
#         "fields": (
#             "email_sent",
#             "email_sent_at",
#         ),
#     },
# ),
#     )

#     ordering = (
#         "-billing_year",
#         "-billing_month",
#     )

#     list_per_page = 25

#     @admin.display(
#         description="Billing Period",
#     )
#     def billing_period(self, obj):
#         return f"{obj.billing_month:02d}/{obj.billing_year}"
    
    
#     @admin.display(description="Email")
#     def email_status(self, obj):
#         if obj.email_sent:
#             return "Sent"

#         return "Not Sent"

#     @admin.display(
#         description="Customer",
#     )
#     def customer_name(self, obj):
#         user = obj.subscription.user

#         if hasattr(user, "get_full_name"):
#             name = user.get_full_name()

#             if name:
#                 return name

#         return user.email
    




# @admin.register(MilkBill)
# class MilkBillAdmin(admin.ModelAdmin):

#     list_display = (
#         "billing_period",
#         "customer_name",
#         "total_amount",
#         "paid_amount",
#         "pending_amount",
#         "status",
#         "payment_date",
#         "email_status",
#     )

#     list_display_links = (
#         "billing_period",
#     )

#     search_fields = (
#         "subscription__subscription_number",
#         "subscription__user__email",
#         "subscription__user__full_name",
#         "subscription__user__phone",
#     )

#     list_filter = (
#         "status",
#         "billing_year",
#         "billing_month",
#         "payment_date",
#     )

#     autocomplete_fields = (
#         "subscription",
#     )

#     readonly_fields = (
#         "pending_amount",
#         "email_sent",
#         "email_sent_at",
#         "created_at",
#         "updated_at",
#     )

#     fieldsets = (
#         (
#             "Bill Information",
#             {
#                 "fields": (
#                     "subscription",
#                     "billing_month",
#                     "billing_year",
#                 )
#             },
#         ),

#         (
#             "Amount",
#             {
#                 "fields": (
#                     "total_amount",
#                     "paid_amount",
#                     "pending_amount",
#                 )
#             },
#         ),

#         (
#             "Cash Payment",
#             {
#                 "fields": (
#                     "status",
#                     "payment_date",
#                     "notes",
#                 )
#             },
#         ),

#         (
#             "Email Information",
#             {
#                 "fields": (
#                     "email_sent",
#                     "email_sent_at",
#                 ),
#             },
#         ),

#         (
#             "System Information",
#             {
#                 "fields": (
#                     "created_at",
#                     "updated_at",
#                 ),
#                 "classes": ("collapse",),
#             },
#         ),
#     )

#     ordering = (
#         "-billing_year",
#         "-billing_month",
#     )

#     list_per_page = 25

#     @admin.display(
#         description="Billing Period",
#     )
#     def billing_period(self, obj):
#         return f"{obj.billing_month:02d}/{obj.billing_year}"

#     @admin.display(
#         description="Email",
#     )
#     def email_status(self, obj):
#         if obj.email_sent:
#             return "Sent"

#         return "Not Sent"

#     @admin.display(
#         description="Customer",
#     )
#     def customer_name(self, obj):
#         user = obj.subscription.user

#         if hasattr(user, "get_full_name"):
#             name = user.get_full_name()

#             if name:
#                 return name

#         return user.email

















from django.utils.html import format_html

@admin.register(MilkBill)
class MilkBillAdmin(admin.ModelAdmin):

    # list_display = (
    #     "billing_period",
    #     "customer_name",
    #     "total_amount",
    #     "paid_amount",
    #     "pending_amount",
    #     "status",
    #     "payment_date",
    #     "email_status",
    #     "payment_action",
    # )
    
    list_display = (
    "billing_period",
    "customer_name",
    "total_amount",
    "paid_amount",
    "pending_amount",
    "status",
    "payment_date",
    "email_status",
    "payment_action",
    "collection_report_link",
)

    list_display_links = (
        "billing_period",
    )

    search_fields = (
        "subscription__subscription_number",
        "subscription__user__email",
        "subscription__user__full_name",
        "subscription__user__phone",
    )

    list_filter = (
        "status",
        "billing_year",
        "billing_month",
        "payment_date",
    )

    autocomplete_fields = (
        "subscription",
    )

    readonly_fields = (
        "pending_amount",
        "email_sent",
        "email_sent_at",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Bill Information",
            {
                "fields": (
                    "subscription",
                    "billing_month",
                    "billing_year",
                )
            },
        ),

        (
            "Amount",
            {
                "fields": (
                    "total_amount",
                    "paid_amount",
                    "pending_amount",
                )
            },
        ),

        (
            "Cash Payment",
            {
                "fields": (
                    "status",
                    "payment_date",
                    "notes",
                )
            },
        ),

        (
            "Email Information",
            {
                "fields": (
                    "email_sent",
                    "email_sent_at",
                ),
            },
        ),

        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    ordering = (
        "-billing_year",
        "-billing_month",
    )

    list_per_page = 25

    # ==================================================
    # CUSTOM ADMIN URLS
    # ==================================================

    # def get_urls(self):

    #     urls = super().get_urls()

    #     custom_urls = [
    #         path(
    #             "<int:bill_id>/record-payment/",
    #             self.admin_site.admin_view(
    #                 self.record_cash_payment
    #             ),
    #             name="milk-bill-record-payment",
    #         ),
    #     ]

    #     return custom_urls + urls
    
    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "collection-report/",
                self.admin_site.admin_view(self.collection_report),
                name="milk-collection-report",
            ),
            path(
                "<int:bill_id>/record-payment/",
                self.admin_site.admin_view(self.record_cash_payment),
                name="milk-bill-record-payment",
            ),
        ]

        return custom_urls + urls

    def collection_report(self, request):

        from decimal import Decimal
        from django.db.models import Sum

        today = timezone.localdate()

        try:
            month = int(request.GET.get("month", today.month))
            year = int(request.GET.get("year", today.year))
        except (TypeError, ValueError):
            month = today.month
            year = today.year

        if month < 1 or month > 12:
            month = today.month

        if year < 2000 or year > 2100:
            year = today.year
            
        
        search = request.GET.get("search", "").strip()

        # bills = (
        #     MilkBill.objects
        #     .filter(
        #         billing_month=month,
        #         billing_year=year,
        #     )
        #     .select_related(
        #         "subscription",
        #         "subscription__user",
        #     )
        #     .order_by(
        #         "-pending_amount",
        #         "subscription__user__full_name",
        #     )
        # )
        bills = (
    MilkBill.objects
    .filter(
        billing_month=month,
        billing_year=year,
    )
    .select_related(
        "subscription",
        "subscription__user",
    )
)
        
        if search:
            from django.db.models import Q

            bills = bills.filter(
                Q(subscription__subscription_number__icontains=search)
                | Q(subscription__user__full_name__icontains=search)
                | Q(subscription__user__email__icontains=search)
                | Q(subscription__user__phone__icontains=search)
            )
            
        
        bills = bills.order_by(
    "-pending_amount",
    "subscription__user__full_name",
)

        total_billed = (
            bills.aggregate(
                total=Sum("total_amount")
            )["total"]
            or Decimal("0.00")
        )

        total_collected = (
            bills.aggregate(
                total=Sum("paid_amount")
            )["total"]
            or Decimal("0.00")
        )

        total_pending = (
            bills.aggregate(
                total=Sum("pending_amount")
            )["total"]
            or Decimal("0.00")
        )

        total_bills = bills.count()

        paid_bills = bills.filter(
            status="paid"
        ).count()

        partial_bills = bills.filter(
            status="partial"
        ).count()

        pending_bills = bills.filter(
            status="pending"
        ).count()

        context = {
            **self.admin_site.each_context(request),

            "title": "Milk Collection Report",

            "month": month,
            "year": year,

            "bills": bills,

            "total_billed": total_billed,
            "total_collected": total_collected,
            "total_pending": total_pending,

            "total_bills": total_bills,
            "paid_bills": paid_bills,
            "partial_bills": partial_bills,
            "pending_bills": pending_bills,

            "month_choices": range(1, 13),
            "year_choices": range(
                today.year - 2,
                today.year + 2,
            ),
        }

        return render(
            request,
            "admin/rdf_app/milk_collection_report.html",
            context,
        )
    # ==================================================
    # RECORD CASH PAYMENT
    # ==================================================

    def record_cash_payment(
        self,
        request,
        bill_id,
    ):

        bill = (
            MilkBill.objects
            .select_related(
                "subscription",
                "subscription__user",
            )
            .filter(id=bill_id)
            .first()
        )

        if not bill:

            self.message_user(
                request,
                "Milk bill not found.",
                level=messages.ERROR,
            )

            return redirect(
                "admin:rdf_app_milkbill_changelist"
            )

        # ----------------------------------------------
        # ALREADY PAID
        # ----------------------------------------------

        if bill.pending_amount <= Decimal("0.00"):

            self.message_user(
                request,
                "This bill is already fully paid.",
                level=messages.WARNING,
            )

            return redirect(
                "admin:rdf_app_milkbill_changelist"
            )

        # ----------------------------------------------
        # POST PAYMENT
        # ----------------------------------------------

        if request.method == "POST":

            payment_amount_raw = (
                request.POST.get("payment_amount", "")
                .strip()
            )

            if not payment_amount_raw:

                messages.error(
                    request,
                    "Please enter a payment amount.",
                )

            else:

                try:

                    payment_amount = Decimal(
                        payment_amount_raw
                    )

                except Exception:

                    payment_amount = None

                    messages.error(
                        request,
                        "Please enter a valid payment amount.",
                    )

                if payment_amount is not None:

                    # ----------------------------------
                    # NEGATIVE / ZERO
                    # ----------------------------------

                    if payment_amount <= Decimal("0.00"):

                        messages.error(
                            request,
                            "Payment amount must be greater than zero.",
                        )

                    # ----------------------------------
                    # OVERPAYMENT
                    # ----------------------------------

                    elif payment_amount > bill.pending_amount:

                        messages.error(
                            request,
                            (
                                f"Payment cannot exceed the "
                                f"pending amount of "
                                f"₹{bill.pending_amount}."
                            ),
                        )

                    else:

                        # ----------------------------------
                        # UPDATE PAYMENT
                        # ----------------------------------

                        bill.paid_amount = (
                            bill.paid_amount
                            + payment_amount
                        )

                        bill.save()

                        self.message_user(
                            request,
                            (
                                f"Cash payment of "
                                f"₹{payment_amount} recorded "
                                f"successfully."
                            ),
                            level=messages.SUCCESS,
                        )

                        return redirect(
                            "admin:rdf_app_milkbill_changelist"
                        )

        # ----------------------------------------------
        # PAYMENT PAGE
        # ----------------------------------------------

        customer_name = (
            bill.subscription.user.full_name
            or bill.subscription.user.email
        )

        context = {
            **self.admin_site.each_context(request),

            "title": "Record Cash Payment",

            "bill": bill,

            "customer_name": customer_name,

            "payment_amount": request.POST.get(
                "payment_amount",
                "",
            ),

            "opts": self.model._meta,

            "has_view_permission": self.has_view_permission(
                request,
                bill,
            ),

        }

        return render(
            request,
            "admin/rdf_app/record_milk_payment.html",
            context,
        )

    # ==================================================
    # LIST DISPLAY HELPERS
    # ==================================================

    @admin.display(
        description="Billing Period",
    )
    def billing_period(self, obj):

        return (
            f"{obj.billing_month:02d}/"
            f"{obj.billing_year}"
        )

    @admin.display(
        description="Email",
    )
    def email_status(self, obj):

        if obj.email_sent:
            return "Sent"

        return "Not Sent"

    @admin.display(
        description="Customer",
        ordering="subscription__user__full_name",
    )
    def customer_name(self, obj):

        user = obj.subscription.user

        if user.full_name:
            return user.full_name

        return user.email
    
    
    @admin.display(
    description="Collection Report"
)
    def collection_report_link(self, obj):
        return format_html(
            '<a class="button" href="{}">Open Report</a>',
            reverse("admin:milk-collection-report"),
        )
    
    

    @admin.display(
        description="Payment",
    )
    def payment_action(self, obj):

        if obj.pending_amount <= Decimal("0.00"):
            return "Paid"

        url = reverse(
            "admin:milk-bill-record-payment",
            args=[obj.id],
        )

        return format_html(
            '<a class="button" href="{}">'
            'Record Cash Payment'
            '</a>',
            url,
        )
