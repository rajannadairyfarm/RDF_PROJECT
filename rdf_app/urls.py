
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
# from .views import user_form_view
from . import views

urlpatterns = [
    path('',views.index, name="index"),
    
    path('temp/',views.temp, name="temp"),
    
        # path('login',views.login, name="login"),
        path('register/', views.register, name="register"),
        # path('contactus/', views.contactus, name="contactus"),
        path("contactus/", views.contactus, name="contactus"),
        path('ourstory/',views.ourstory, name="ourstory"),
        
        path('aboutus/', views.aboutus, name="aboutus"),
        # path('subscribe/', views.subscribe, name="subscribe"),
        path('privacy_policy/',views.privacy_policy, name="privacy_policy"),
        path('terms_conditions/',views.terms_conditions, name="terms_conditions"),
        
        path('user_profile/',views.user_profile,name="user_profile"),
        #   path('dashboard/',views.dashboard,name="dashboard"),
                
        
        
        path(
    "subscribe/",
    views.subscribe,
    name="subscribe"
),
        
        
        
        
        
        
        
        
        
        path( "register/", views.register, name="register" ), 
        path( "registration-success/", views.registration_success, name="registration-success" ),
        path( "verify-email/<uuid:token>/", views.verify_email, name="verify-email" ),
        
        path( "login/", views.user_login, name="login" ),
   
#    path( "resend-verification/", views.resend_verification_email, name="resend-verification" ),

path(
    "resend-verification/",
    views.resend_verification_email,
    name="resend-verification"
),
path(
    "resend-verification-by-email/",
    views.resend_verification_by_email,
    name="resend-verification-by-email"
),



path(
    "forgot-password/",
    views.forgot_password,
    name="forgot-password"
),

path(
    "reset-password/<uuid:token>/",
    views.reset_password,
    name="reset-password"
),
path("profile/",views.profile, name="profile"),




path("shop/", views.shop, name="shop"),

path(
    "shop/filter/",
    views.shop_filter,
    name="shop-filter",
),

path(
    "shop/product/<slug:slug>/",
    views.product_detail,
    name="product-detail"
),

path(
    "shop/category/<slug:slug>/",
    views.category_products,
    name="category-products"
),

path( "cart/add/<str:product_id>/", views.cart_add, name="cart-add" ),

path(
    "cart/",
    views.cart,
    name="cart"
),
path(
    "cart/update/<str:product_id>/",
    views.cart_update,
    name="cart-update"
),

path(
    "cart/remove/<str:product_id>/",
    views.cart_remove,
    name="cart-remove"
),


path(
    "addresses/",
    views.address_list,
    name="addresses"
),

path(
    "addresses/add/",
    views.address_add,
    name="address-add"
),

path(
    "addresses/<int:address_id>/edit/",
    views.address_edit,
    name="address-edit"
),

path(
    "addresses/<int:address_id>/delete/",
    views.address_delete,
    name="address-delete"
),

path(
    "addresses/<int:address_id>/default/",
    views.address_set_default,
    name="address-set-default"
),


path(
    "checkout/",
    views.checkout,
    name="checkout"
),


path(
    "checkout/place-order/",
    views.place_order,
    name="place-order"
),

path(
    "order/success/<str:order_number>/",
    views.order_success,
    name="order-success"
),

path(
    "orders/",
    views.my_orders,
    name="orders"
),

path(
    "orders/<str:order_number>/",
    views.order_detail,
    name="order-detail"
),

path(
    "orders/<str:order_number>/track/",
    views.order_tracking,
    name="order-tracking"
),

path("logout/", views.user_logout, name="logout"),














path(
    "my-milk/",
    views.my_milk_subscription,
    name="my-milk-subscription",
),

path(
    "milk/subscribe/",
    views.create_milk_subscription,
    name="create-milk-subscription",
),



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)