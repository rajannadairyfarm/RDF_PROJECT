# rdf_app/context_processors.py
from .models import Cart

def cart_count(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        count = sum(item.quantity for item in cart.items.filter(product__is_active=True))
    else:
        session_cart = request.session.get("cart", {})
        count = sum(int(qty) for qty in session_cart.values() if int(qty) > 0)
        
        
    # print("cart count==",count)
    return {"cart_count": count}


