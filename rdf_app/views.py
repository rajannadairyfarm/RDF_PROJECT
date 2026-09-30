from decimal import Decimal

from django.shortcuts import render

# Create your views here.




import resend
from django.conf import settings

resend.api_key = settings.RESEND_API_KEY



from django.db import transaction
from decimal import Decimal

def merge_session_cart_to_database(request):
    """
    Merge the guest session cart into the logged-in user's
    database cart.

    Existing database quantities are combined with the
    guest cart quantities while respecting current stock.
    """

    session_cart = request.session.get("cart", {})

    if not session_cart:
        return

    if not request.user.is_authenticated:
        return

    with transaction.atomic():

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        product_ids = list(session_cart.keys())

        products = (
            Product.objects
            .select_related("category")
            .filter(
                product_id__in=product_ids,
                is_active=True
            )
        )

        product_map = {
            str(product.product_id): product
            for product in products
        }

        for product_id, session_quantity in session_cart.items():

            product = product_map.get(
                str(product_id)
            )

            if not product:
                continue

            # Product unavailable
            if (
                not product.is_in_stock
                or product.stock_quantity <= 0
            ):
                continue

            try:
                session_quantity = int(
                    session_quantity
                )
            except (TypeError, ValueError):
                continue

            if session_quantity < 1:
                continue

            # Never exceed available stock
            session_quantity = min(
                session_quantity,
                int(product.stock_quantity)
            )

            if session_quantity < 1:
                continue

            cart_item = (
                CartItem.objects
                .filter(
                    cart=cart,
                    product=product
                )
                .first()
            )

            if cart_item:

                new_quantity = (
                    cart_item.quantity
                    + session_quantity
                )

                new_quantity = min(
                    new_quantity,
                    int(product.stock_quantity)
                )

                cart_item.quantity = new_quantity

                cart_item.save(
                    update_fields=[
                        "quantity",
                        "updated_at"
                    ]
                )

            else:

                CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=session_quantity
                )

    # Session cart has now been merged
    request.session.pop("cart", None)
    request.session.modified = True
    
    
    

def index(request):
    return render(request, "loading_page.html")




def temp(request):
    return render(request, "temp.html")


# def contactus(request):
#     return render(request, "contactus.html")



from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect


def contactus(request):

    if request.method == "POST":

        full_name = request.POST.get("fullname", "").strip()
        email = request.POST.get("email", "").strip().lower()
        phone_number = request.POST.get("phone", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        # -------------------------
        # Validation
        # -------------------------

        if not full_name:
            messages.error(request, "Full name is required.")
            return redirect("contactus")

        if not email:
            messages.error(request, "Email address is required.")
            return redirect("contactus")

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return redirect("contactus")

        if not phone_number:
            messages.error(request, "Phone number is required.")
            return redirect("contactus")

        if not phone_number.isdigit() or len(phone_number) != 10:
            messages.error(
                request,
                "Please enter a valid 10-digit phone number."
            )
            return redirect("contactus")

        if not subject:
            messages.error(request, "Subject is required.")
            return redirect("contactus")

        if not message:
            messages.error(request, "Message is required.")
            return redirect("contactus")

        # -------------------------
        # Email to Rajanna Dairy Farm
        # -------------------------

#         try:
            

#             # -------------------------
#             # Admin email
#             # -------------------------
#             admin_html = f"""
#             <h2>New Contact Us Message</h2>
#             <p><strong>Full Name:</strong> {full_name}</p>
#             <p><strong>Email:</strong> {email}</p>
#             <p><strong>Phone Number:</strong> {phone_number}</p>
#             <p><strong>Subject:</strong> {subject}</p>
#             <p><strong>Message:</strong><br>{message}</p>
#             """

#             resend.Emails.send({
#                 "from": "Rajanna Dairy Farm <rajannadairyfarm@gmail.com>",
#                 "to": [settings.DEFAULT_FROM_EMAIL],
#                 "subject": f"Contact Us: {subject}",
#                 "html": admin_html,
#                 "reply_to": [email],
#             })

#             # -------------------------
#             # Customer confirmation email
#             # -------------------------
#             customer_html = f"""
#             <p>Dear {full_name},</p>

#             <p>Thank you for contacting <strong>Rajanna Dairy Farm</strong>.</p>

#             <p>We have received your message successfully.<br>
#             Our team will review your message and contact you soon.</p>

#             <p>Thank you for choosing Rajanna Dairy Farm.</p>

#             <p>Regards,<br>
#             Rajanna Dairy Farm</p>
#             """

#             resend.Emails.send({
#                 "from": "Rajanna Dairy Farm <rajannadairyfarm@gmail.com>",
#                 "to": [email],
#                 "subject": "We received your message - Rajanna Dairy Farm",
#                 "html": customer_html,
#             })


# #             admin_email = EmailMessage(
# #                 subject=f"Contact Us: {subject}",
# #                 body=f"""
# # New Contact Us Message

# # Full Name:
# # {full_name}

# # Email:
# # {email}

# # Phone Number:
# # {phone_number}

# # Subject:
# # {subject}

# # Message:
# # {message}
# # """,
# #                 from_email=settings.DEFAULT_FROM_EMAIL,
# #                 to=[settings.DEFAULT_FROM_EMAIL],
# #                 reply_to=[email],
# #             )

# #             admin_email.send(fail_silently=False)

# #             # -------------------------
# #             # Confirmation email
# #             # -------------------------

# #             customer_email = EmailMessage(
# #                 subject="We received your message - Rajanna Dairy Farm",
# #                 body=f"""
# # Dear {full_name},

# # Thank you for contacting Rajanna Dairy Farm.

# # We have received your message successfully.

# # Our team will review your message and contact you soon.

# # Thank you for choosing Rajanna Dairy Farm.

# # Regards,
# # Rajanna Dairy Farm
# # """,
# #                 from_email=settings.DEFAULT_FROM_EMAIL,
# #                 to=[email],
# #             )

# #             customer_email.send(fail_silently=False)

#             messages.success(
#                 request,
#                 "Your message has been sent successfully. "
#                 "We will contact you soon."
#             )

#         except Exception:
#             messages.error(
#                 request,
#                 "Unable to send your message right now. "
#                 "Please try again later."
#             )


        try:
            admin_html = f"""
            <h2>New Contact Us Message</h2>
            <p><strong>Full Name:</strong> {full_name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Phone Number:</strong> {phone_number}</p>
            <p><strong>Subject:</strong> {subject}</p>
            <p><strong>Message:</strong><br>{message}</p>
            """

            admin_result = resend.Emails.send({
                "from": "Rajanna Dairy Farm <onboarding@resend.dev>",
                "to": [settings.DEFAULT_FROM_EMAIL],
                "subject": f"Contact Us: {subject}",
                "html": admin_html,
                "reply_to": email,
            })

            print("ADMIN EMAIL RESULT:", admin_result)

            customer_html = f"""
            <p>Dear {full_name},</p>

            <p>Thank you for contacting
            <strong>Rajanna Dairy Farm</strong>.</p>

            <p>
                We have received your message successfully.<br>
                Our team will review your message and contact you soon.
            </p>

            <p>Thank you for choosing Rajanna Dairy Farm.</p>

            <p>
                Regards,<br>
                Rajanna Dairy Farm
            </p>
            """

            customer_result = resend.Emails.send({
                "from": "Rajanna Dairy Farm <onboarding@resend.dev>",
                "to": [email],
                "subject": "We received your message - Rajanna Dairy Farm",
                "html": customer_html,
            })

            print("CUSTOMER EMAIL RESULT:", customer_result)

            messages.success(
                request,
                "Your message has been sent successfully. "
                "We will contact you soon."
            )

        except Exception as e:
            print("CONTACT EMAIL ERROR:", repr(e))

            messages.error(
                request,
                "Unable to send your message right now. "
                "Please try again later."
            )

        return redirect("contactus")

    return render(request, "contactus.html")






def ourstory(request):
    return render(request, "ourstory.html")



def aboutus(request):
    return render(request, "aboutus.html")



# def subscribe(request):
#     return render(request, "subscribe.html")



def privacy_policy(request):
    return render(request, "privacy_policy.html")


def terms_conditions(request):
    return render(request, "terms_conditions.html")























import re
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import Address, Cart, CartItem, Category, Product, User, EmailVerificationToken


from .models import UserProfile

@require_http_methods(["GET", "POST"])
def register(request):

    if request.user.is_authenticated:
        return redirect("shop")

    if request.method == "GET":
        return render(request, "register.html")

    # ------------------------------------------------
    # Get form data
    # ------------------------------------------------

    full_name = request.POST.get("full_name", "").strip()
    email = request.POST.get("email", "").strip().lower()
    phone = request.POST.get("phone", "").strip()
    password = request.POST.get("password", "")
    confirm_password = request.POST.get("confirm_password", "")

    errors = []

    # ------------------------------------------------
    # Full name validation
    # ------------------------------------------------

    if not full_name:
        errors.append("Full name is required.")

    elif len(full_name) < 2:
        errors.append("Full name must contain at least 2 characters.")

    elif len(full_name) > 150:
        errors.append("Full name cannot exceed 150 characters.")

    elif not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s.'-]+$", full_name):
        errors.append("Full name contains invalid characters.")

    # ------------------------------------------------
    # Email validation
    # ------------------------------------------------

    if not email:
        errors.append("Email address is required.")

    elif len(email) > 254:
        errors.append("Email address is too long.")

    elif not re.match(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
        email
    ):
        errors.append("Please enter a valid email address.")

    elif User.objects.filter(email__iexact=email).exists():
        errors.append("An account with this email already exists.")

    # ------------------------------------------------
    # Phone validation
    # ------------------------------------------------

    if not phone:
        errors.append("Phone number is required.")

    else:

        # Remove spaces, hyphens and brackets
        normalized_phone = re.sub(r"[\s\-()]", "", phone)

        # Indian phone number / international format
        if not re.match(r"^\+?[0-9]{10,15}$", normalized_phone):
            errors.append("Please enter a valid phone number.")

        elif User.objects.filter(phone=normalized_phone).exists():
            errors.append("An account with this phone number already exists.")

        phone = normalized_phone

    # ------------------------------------------------
    # Password validation
    # ------------------------------------------------

    if not password:
        errors.append("Password is required.")

    if not confirm_password:
        errors.append("Please confirm your password.")

    if password and confirm_password:

        if password != confirm_password:
            errors.append("Passwords do not match.")

    # Django password validators
    # if password and not errors:

    #     try:
    #         validate_password(password)
    #     except ValidationError as e:
    #         errors.extend(e.messages)

    # ------------------------------------------------
    # Return validation errors
    # ------------------------------------------------

    if errors:

        for error in errors:
            messages.error(request, error)

        return render(
            request,
            "register.html",
            {
                "full_name": full_name,
                "email": email,
                "phone": phone,
            }
        )

    # ------------------------------------------------
    # Create user
    # ------------------------------------------------

    try:
        print("1111111111")

        with transaction.atomic():
            print("222222222")

            # Create inactive user
            user = User.objects.create_user(
                email=email,
                full_name=full_name,
                phone=phone,
                password=password,
                is_active=False
            )
            
            Subscriber.objects.get_or_create(
    email=user.email.strip().lower()
)
            
            UserProfile.objects.create(
    user=user
)
            # print("user==",user)

            # Remove old unused verification tokens
            EmailVerificationToken.objects.filter(
                user=user,
                is_used=False
            ).delete()

            # Token valid for 5 minutes
            verification_token = EmailVerificationToken.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(minutes=5)
            )
            print("verification token===",verification_token)

    except IntegrityError:
        print("333333333")

        messages.error(
            request,
            "An account with these details already exists."
        )

        return render(
            request,
            "register.html",
            {
                "full_name": full_name,
                "email": email,
                "phone": phone,
            }
        )

    # ------------------------------------------------
    # Build verification URL
    # ------------------------------------------------
    print("444444444444")
    verification_url = request.build_absolute_uri(
        reverse(
            "verify-email",
            kwargs={
                "token": str(verification_token.token)
            }
        )
    )
    print("5555555555555")
    # ------------------------------------------------
    # Email content
    # ------------------------------------------------

    subject = "Verify your Rajanna Dairy Farm account"

    context = {
        "user": user,
        "verification_url": verification_url,
    }

    html_message = render_to_string(
        "verify_email.html",
        context
    )

    text_message = (
        f"Hello {user.full_name},\n\n"
        f"Please verify your email address by opening this link:\n\n"
        f"{verification_url}\n\n"
        f"This link will expire in 5 minutes.\n\n"
        f"If you did not create this account, please ignore this email.\n\n"
        f"Rajanna Dairy Farm"
    )
    
    print("user email===", user.email)
    print("settings.DEFAULT_FROM_EMAIL===",settings.DEFAULT_FROM_EMAIL)
    # ------------------------------------------------
    # Send email
    # ------------------------------------------------

    try:
        print("6666667777777777777")

        # email_message = EmailMultiAlternatives(
        #     subject=subject,
        #     body=text_message,
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     to=[user.email],
        # )

        # email_message.attach_alternative(
        #     html_message,
        #     "text/html"
        # )

        # email_message.send(
        #     fail_silently=False
        # )
        
        resend.Emails.send({
            "from": "Rajanna Dairy Farm <onboarding@resend.dev>",
            "to": [user.email],
            "subject": subject,
            "text": text_message,   # plain text fallback
            "html": html_message,   # HTML version
        })

    except Exception as e:

        # Delete user/token if email couldn't be sent
        user.delete()
        print("exception===",e)

        messages.error(
            request,
            "We could not send the verification email. "
            "Please try again."
        )

        return render(
            request,
            "register.html",
            {
                "full_name": full_name,
                "email": email,
                "phone": phone,
            }
        )

    # ------------------------------------------------
    # Success
    # ------------------------------------------------
    request.session["pending_verification_user_id"] = user.user_id
    request.session.set_expiry(60 * 30)
    
    messages.success(
        request,
        "Registration successful! "
        "Please check your email and verify your account."
    )

    return redirect("registration-success")






def registration_success(request):
    return render(
        request,
        "registration_success.html"
    )
















def verify_email(request, token):

    try:

        verification_token = (
            EmailVerificationToken.objects
            .select_related("user")
            .get(token=token)
        )

    except EmailVerificationToken.DoesNotExist:

        return render(
            request,
            "email_verification_failed.html",
            {
                "message": "This verification link is invalid."
            }
        )

    # Token already used
    if verification_token.is_used:

        return render(
            request,
            "email_verification_failed.html",
            {
                "message": "This verification link has already been used."
            }
        )

    # Token expired
    if timezone.now() >= verification_token.expires_at:

        return render(
            request,
            "email_verification_failed.html",
            {
                "message": (
                    "This verification link has expired. "
                    "Please request a new verification email."
                )
            }
        )

    user = verification_token.user

    # Activate user
    user.is_active = True
    user.save(
        update_fields=["is_active"]
    )

    # Mark token as used
    verification_token.is_used = True
    verification_token.save(
        update_fields=["is_used"]
    )

    # Log user in
    login(
        request,
        user,
        backend="django.contrib.auth.backends.ModelBackend"
    )
    merge_session_cart_to_database(request)
    
    

    # Store useful session information
    request.session["user_id"] = user.user_id
    request.session["user_email"] = user.email
    request.session["user_name"] = user.full_name

    # Make session persistent
    request.session.set_expiry(
        settings.SESSION_COOKIE_AGE
    )

    return redirect("shop")



import re

from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import User


@require_http_methods(["GET", "POST"])
def user_login(request):
    
    # Consume messages immediately so they don’t leak
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # iterating clears them

    # ---------------------------------------------
    # Already logged in
    # ---------------------------------------------

    if request.user.is_authenticated:
        return redirect("shop")

    # ---------------------------------------------
    # GET request
    # ---------------------------------------------

    if request.method == "GET":
        return render(
            request,
            "login.html"
        )

    # ---------------------------------------------
    # Get submitted data
    # ---------------------------------------------

    email = request.POST.get(
        "email",
        ""
    ).strip().lower()

    password = request.POST.get(
        "password",
        ""
    )

    errors = []

    # ---------------------------------------------
    # Email validation
    # ---------------------------------------------

    if not email:

        errors.append(
            "Email address is required."
        )

    elif len(email) > 254:

        errors.append(
            "Please enter a valid email address."
        )

    elif not re.match(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
        email
    ):

        errors.append(
            "Please enter a valid email address."
        )

    # ---------------------------------------------
    # Password validation
    # ---------------------------------------------

    if not password:

        errors.append(
            "Password is required."
        )

    # ---------------------------------------------
    # Return validation errors
    # ---------------------------------------------

    if errors:

        for error in errors:
            messages.error(
                request,
                error
            )

        return render(
            request,
            "login.html",
            {
                "email": email,
            }
        )

    # ---------------------------------------------
    # Find user
    # ---------------------------------------------

    try:

        user = User.objects.get(
            email__iexact=email
        )

    except User.DoesNotExist:

        messages.error(
            request,
            "Invalid email or password."
        )

        return render(
            request,
            "login.html",
            {
                "email": email,
            }
        )

    # ---------------------------------------------
    # Check email verification / account status
    # ---------------------------------------------

    if not user.is_active:

        messages.warning(
            request,
            "Your email address has not been verified yet. "
    
        )

        return render(
            request,
            "login.html",
            {
                "email": email,
                "show_resend_verification": True
            }
        )

    # ---------------------------------------------
    # Check password
    # ---------------------------------------------

    if not user.check_password(password):

        messages.error(
            request,
            "Invalid email or password."
        )

        return render(
            request,
            "login.html",
            {
                "email": email,
            }
        )

    # ---------------------------------------------
    # Successful authentication
    # ---------------------------------------------

    login(
        request,
        user,
        backend="django.contrib.auth.backends.ModelBackend"
    )
#     login(
#     request,
#     user,
#     backend="django.contrib.auth.backends.ModelBackend"
# )

    merge_session_cart_to_database(request)

    # ---------------------------------------------
    # Store useful session information
    # ---------------------------------------------

    request.session["user_id"] = user.user_id
    request.session["user_email"] = user.email
    request.session["user_name"] = user.full_name

    # ---------------------------------------------
    # Session expiry
    # ---------------------------------------------

    request.session.set_expiry(
        60 * 60 * 24 * 7
    )

    # ---------------------------------------------
    # Redirect dashboard
    # ---------------------------------------------

    return redirect("shop")




import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import User, EmailVerificationToken


@require_POST
def resend_verification_email(request):

    user_id = request.session.get(
        "pending_verification_user_id"
    )
    print(user_id)

    if not user_id:
        messages.error(
            request,
            "Your verification session has expired. Please register again."
        )
        return redirect("register")

    try:
        user = User.objects.get(
            user_id=user_id
        )
    except User.DoesNotExist:
        request.session.pop(
            "pending_verification_user_id",
            None
        )

        messages.error(
            request,
            "Unable to find your registration. Please register again."
        )

        return redirect("register")

    # Already verified
    if user.is_active:
        request.session.pop(
            "pending_verification_user_id",
            None
        )

        messages.info(
            request,
            "Your email has already been verified. You can login."
        )

        return redirect("login")

    # 60-second resend cooldown
    latest_token = (
        EmailVerificationToken.objects
        .filter(user=user)
        .order_by("-created_at")
        .first()
    )

    if latest_token:

        elapsed = (
            timezone.now() - latest_token.created_at
        ).total_seconds()

        if elapsed < 60:

            remaining = int(60 - elapsed)

            messages.warning(
                request,
                f"Please wait {remaining} seconds before "
                "requesting another verification email."
            )

            return redirect(
                "registration-success"
            )

    try:

        with transaction.atomic():

            # Invalidate previous unused tokens
            EmailVerificationToken.objects.filter(
                user=user,
                is_used=False
            ).update(
                is_used=True
            )

            # Create new token
            verification_token = (
                EmailVerificationToken.objects.create(
                    user=user,
                    expires_at=(
                        timezone.now()
                        + timedelta(minutes=30)
                    )
                )
            )

    except Exception:

        messages.error(
            request,
            "Something went wrong. Please try again later."
        )

        return redirect(
            "registration-success"
        )

    # Verification URL
    verification_url = request.build_absolute_uri(
        reverse(
            "verify-email",
            kwargs={
                "token": str(
                    verification_token.token
                )
            }
        )
    )

    subject = (
        "Verify your Rajanna Dairy Farm account"
    )

    context = {
        "user": user,
        "verification_url": verification_url,
    }

    html_message = render_to_string(
        "verify_email.html",
        context
    )

    text_message = (
        f"Hello {user.full_name},\n\n"
        "Please verify your email address using "
        "the link below:\n\n"
        f"{verification_url}\n\n"
        "This link will expire in 30 minutes.\n\n"
        "If you did not create this account, "
        "please ignore this email.\n\n"
        "Rajanna Dairy Farm"
    )

    try:

        # email_message = EmailMultiAlternatives(
        #     subject=subject,
        #     body=text_message,
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     to=[user.email],
        # )

        # email_message.attach_alternative(
        #     html_message,
        #     "text/html"
        # )

        # email_message.send(
        #     fail_silently=False
        # )
        
        resend.Emails.send({
    "from": "Rajanna Dairy Farm <onboarding@resend.dev>",
    "to": [user.email],
    "subject": subject,
    "text": text_message,   # plain text fallback
    "html": html_message,   # HTML version
})

    except Exception:

        verification_token.is_used = True

        verification_token.save(
            update_fields=["is_used"]
        )

        messages.error(
            request,
            "We could not send the verification email. "
            "Please try again later."
        )

        return redirect(
            "registration-success"
        )

    messages.success(
        request,
        f"A new verification email has been sent to {user.email}."
    )

    return redirect(
        "registration-success"
    )
  

import re
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import User, EmailVerificationToken


@require_http_methods(["GET", "POST"])
def resend_verification_by_email(request):

    if request.method == "GET":
        return render(
            request,
            "resend_verification.html"
        )

    email = request.POST.get(
        "email",
        ""
    ).strip().lower()

    # -----------------------------------------
    # Validate email
    # -----------------------------------------

    if not email:
        messages.error(
            request,
            "Please enter your email address."
        )

        return render(
            request,
            "resend_verification.html"
        )

    if len(email) > 254:
        messages.error(
            request,
            "Please enter a valid email address."
        )

        return render(
            request,
            "resend_verification.html",
            {"email": email}
        )

    if not re.match(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
        email
    ):
        messages.error(
            request,
            "Please enter a valid email address."
        )

        return render(
            request,
            "resend_verification.html",
            {"email": email}
        )

    # -----------------------------------------
    # Find user
    # -----------------------------------------

    try:

        user = User.objects.get(
            email__iexact=email
        )

    except User.DoesNotExist:

        # Do not reveal whether account exists
        messages.success(
            request,
            "If an account exists with this email, "
            "a verification email will be sent."
        )

        return redirect(
            "resend-verification-by-email"
        )

    # -----------------------------------------
    # Already verified
    # -----------------------------------------

    if user.is_active:

        messages.info(
            request,
            "This email has already been verified. "
            "You can login to your account."
        )

        return redirect(
            "login"
        )

    # -----------------------------------------
    # Resend cooldown
    # -----------------------------------------

    latest_token = (
        EmailVerificationToken.objects
        .filter(user=user)
        .order_by("-created_at")
        .first()
    )

    if latest_token:

        elapsed = (
            timezone.now()
            - latest_token.created_at
        ).total_seconds()

        if elapsed < 60:

            remaining = int(
                60 - elapsed
            )

            messages.warning(
                request,
                f"Please wait {remaining} seconds "
                "before requesting another "
                "verification email. or you have an active link in you mail check it."
            )

            return render(
                request,
                "resend_verification.html",
                {"email": email}
            )

    # -----------------------------------------
    # Create new verification token
    # -----------------------------------------

    try:

        with transaction.atomic():

            # Invalidate old tokens
            EmailVerificationToken.objects.filter(
                user=user,
                is_used=False
            ).update(
                is_used=True
            )

            # Create new token
            verification_token = (
                EmailVerificationToken.objects.create(
                    user=user,
                    expires_at=(
                        timezone.now()
                        + timedelta(minutes=30)
                    )
                )
            )

    except Exception:

        messages.error(
            request,
            "Something went wrong. "
            "Please try again later."
        )

        return render(
            request,
            "resend_verification.html",
            {"email": email}
        )

    # -----------------------------------------
    # Verification URL
    # -----------------------------------------

    verification_url = request.build_absolute_uri(
        reverse(
            "verify-email",
            kwargs={
                "token": str(
                    verification_token.token
                )
            }
        )
    )

    # -----------------------------------------
    # Email
    # -----------------------------------------

    subject = (
        "Verify your Rajanna Dairy Farm account"
    )

    context = {
        "user": user,
        "verification_url": verification_url,
    }

    html_message = render_to_string(
        "verify_email.html",
        context
    )

    text_message = (
        f"Hello {user.full_name},\n\n"
        "Please verify your email address "
        "using the link below:\n\n"
        f"{verification_url}\n\n"
        "This link will expire in 30 minutes.\n\n"
        "If you did not create this account, "
        "please ignore this email.\n\n"
        "Rajanna Dairy Farm"
    )

    try:

        # email_message = EmailMultiAlternatives(
        #     subject=subject,
        #     body=text_message,
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     to=[user.email],
        # )

        # email_message.attach_alternative(
        #     html_message,
        #     "text/html"
        # )

        # email_message.send(
        #     fail_silently=False
        # )
        resend.Emails.send({
    "from": "Rajanna Dairy Farm <onboarding@resend.dev>",  # replace with your verified sender
    "to": [user.email],
    "subject": subject,
    "text": text_message,   # plain text fallback
    "html": html_message,   # HTML version
})

    except Exception:

        verification_token.is_used = True

        verification_token.save(
            update_fields=["is_used"]
        )

        messages.error(
            request,
            "We could not send the verification email. "
            "Please try again later."
        )

        return render(
            request,
            "resend_verification.html",
            {"email": email}
        )

    # -----------------------------------------
    # Success
    # -----------------------------------------

    messages.success(
        request,
        "A new verification email has been sent. "
        "Please check your inbox."
    )

    return redirect(
        "resend-verification-by-email"
    )





import re

from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import User, PasswordResetToken


@require_http_methods(["GET", "POST"])
def forgot_password(request):

    if request.method == "GET":
        return render(
            request,
            "forgot_password.html"
        )

    email = request.POST.get(
        "email",
        ""
    ).strip().lower()

    # -----------------------------------------
    # Validate email
    # -----------------------------------------

    if not email:

        messages.error(
            request,
            "Please enter your email address."
        )

        return render(
            request,
            "forgot_password.html"
        )

    if len(email) > 254:

        messages.error(
            request,
            "Please enter a valid email address."
        )

        return render(
            request,
            "forgot_password.html",
            {"email": email}
        )

    if not re.match(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
        email
    ):

        messages.error(
            request,
            "Please enter a valid email address."
        )

        return render(
            request,
            "forgot_password.html",
            {"email": email}
        )

    # -----------------------------------------
    # Find user
    # -----------------------------------------

    try:

        user = User.objects.get(
            email__iexact=email
        )

    except User.DoesNotExist:

        # Security:
        # Do not reveal whether an account exists.

        messages.success(
            request,
            "If an account exists with this email, "
            "you will receive a password reset link."
        )

        return redirect(
            "forgot-password"
        )

    # -----------------------------------------
    # If email isn't verified
    # -----------------------------------------

    if not user.is_active:

        messages.success(
            request,
            "If an account exists with this email, "
            "you will receive a password reset link."
        )

        return redirect(
            "forgot-password"
        )

    # -----------------------------------------
    # Prevent rapid reset requests
    # -----------------------------------------

    latest_token = (
        PasswordResetToken.objects
        .filter(user=user)
        .order_by("-created_at")
        .first()
    )

    if latest_token:

        elapsed = (
            timezone.now()
            - latest_token.created_at
        ).total_seconds()

        if elapsed < 60:

            remaining = int(
                60 - elapsed
            )

            messages.warning(
                request,
                f"Please wait {remaining} seconds "
                "before requesting another reset email."
            )

            return render(
                request,
                "forgot_password.html",
                {"email": email}
            )

    # -----------------------------------------
    # Create new reset token
    # -----------------------------------------

    try:

        with transaction.atomic():

            # Invalidate previous tokens
            PasswordResetToken.objects.filter(
                user=user,
                is_used=False
            ).update(
                is_used=True
            )

            reset_token = (
                PasswordResetToken.objects.create(
                    user=user,
                    expires_at=(
                        timezone.now()
                        + timedelta(minutes=30)
                    )
                )
            )

    except Exception:

        messages.error(
            request,
            "Something went wrong. "
            "Please try again later."
        )

        return render(
            request,
            "forgot_password.html",
            {"email": email}
        )

    # -----------------------------------------
    # Build reset URL
    # -----------------------------------------

    reset_url = request.build_absolute_uri(
        reverse(
            "reset-password",
            kwargs={
                "token": str(
                    reset_token.token
                )
            }
        )
    )

    # -----------------------------------------
    # Email content
    # -----------------------------------------

    subject = (
        "Reset your Rajanna Dairy Farm password"
    )

    context = {
        "user": user,
        "reset_url": reset_url,
    }

    html_message = render_to_string(
        "password_reset_email.html",
        context
    )

    text_message = (
        f"Hello {user.full_name},\n\n"
        "We received a request to reset your "
        "Rajanna Dairy Farm account password.\n\n"
        "Reset your password using the link below:\n\n"
        f"{reset_url}\n\n"
        "This link will expire in 30 minutes "
        "and can only be used once.\n\n"
        "If you did not request a password reset, "
        "please ignore this email.\n\n"
        "Rajanna Dairy Farm"
    )

    # -----------------------------------------
    # Send email
    # -----------------------------------------

    try:

        # email_message = EmailMultiAlternatives(
        #     subject=subject,
        #     body=text_message,
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     to=[user.email],
        # )

        # email_message.attach_alternative(
        #     html_message,
        #     "text/html"
        # )

        # email_message.send(
        #     fail_silently=False
        # )
        resend.Emails.send({
    "from": "Rajanna Dairy Farm <onboarding@resend.dev>",  # replace with your verified sender
    "to": [user.email],
    "subject": subject,
    "text": text_message,   # plain text fallback
    "html": html_message,   # HTML version
})

    except Exception:

        reset_token.is_used = True

        reset_token.save(
            update_fields=["is_used"]
        )

        messages.error(
            request,
            "We could not send the password reset email. "
            "Please try again later."
        )

        return render(
            request,
            "forgot_password.html",
            {"email": email}
        )

    # -----------------------------------------
    # Success
    # -----------------------------------------

    messages.success(
        request,
        "If an account exists with this email, "
        "a password reset link has been sent."
    )

    return redirect(
        "forgot-password"
    )





@require_http_methods(["GET", "POST"])
def reset_password(request, token):

    # -----------------------------------------
    # Find token
    # -----------------------------------------

    try:

        reset_token = (
            PasswordResetToken.objects
            .select_related("user")
            .get(token=token)
        )

    except PasswordResetToken.DoesNotExist:

        return render(
            request,
            "password_reset_invalid.html",
            {
                "message":
                    "This password reset link is invalid."
            }
        )

    # -----------------------------------------
    # Check token
    # -----------------------------------------

    if reset_token.is_used:

        return render(
            request,
            "password_reset_invalid.html",
            {
                "message":
                    "This password reset link has already been used."
            }
        )

    if timezone.now() >= reset_token.expires_at:

        return render(
            request,
            "password_reset_invalid.html",
            {
                "message":
                    "This password reset link has expired. "
                    "Please request a new one."
            }
        )

    user = reset_token.user

    # -----------------------------------------
    # GET
    # -----------------------------------------

    if request.method == "GET":

        return render(
            request,
            "reset_password.html",
            {
                "token": token
            }
        )

    # -----------------------------------------
    # POST
    # -----------------------------------------

    password = request.POST.get(
        "password",
        ""
    )

    confirm_password = request.POST.get(
        "confirm_password",
        ""
    )

    # -----------------------------------------
    # Validate password
    # -----------------------------------------

    if not password:

        messages.error(
            request,
            "Please enter a new password."
        )

        return render(
            request,
            "reset_password.html",
            {
                "token": token
            }
        )

    if not confirm_password:

        messages.error(
            request,
            "Please confirm your new password."
        )

        return render(
            request,
            "reset_password.html",
            {
                "token": token
            }
        )

    if password != confirm_password:

        messages.error(
            request,
            "Passwords do not match."
        )

        return render(
            request,
            "reset_password.html",
            {
                "token": token
            }
        )

    # -----------------------------------------
    # Django password validation
    # -----------------------------------------

    from django.contrib.auth.password_validation import (
        validate_password
    )

    try:

        validate_password(
            password,
            user=user
        )

    except Exception as validation_error:

        for error in validation_error:

            messages.error(
                request,
                error
            )

        return render(
            request,
            "reset_password.html",
            {
                "token": token
            }
        )

    # -----------------------------------------
    # Change password
    # -----------------------------------------

    try:

        with transaction.atomic():

            # Re-check token inside transaction
            reset_token = (
                PasswordResetToken.objects
                .select_for_update()
                .select_related("user")
                .get(
                    token=token
                )
            )

            if reset_token.is_used:

                return render(
                    request,
                    "password_reset_invalid.html",
                    {
                        "message":
                            "This password reset link "
                            "has already been used."
                    }
                )

            if timezone.now() >= reset_token.expires_at:

                return render(
                    request,
                    "password_reset_invalid.html",
                    {
                        "message":
                            "This password reset link has expired. "
                            "Please request a new one."
                    }
                )

            user = reset_token.user

            user.set_password(password)

            user.save(
                update_fields=["password"]
            )

            # Invalidate this token
            reset_token.is_used = True

            reset_token.save(
                update_fields=["is_used"]
            )

            # Invalidate all other unused reset tokens
            PasswordResetToken.objects.filter(
                user=user,
                is_used=False
            ).exclude(
                pk=reset_token.pk
            ).update(
                is_used=True
            )

    except PasswordResetToken.DoesNotExist:

        return render(
            request,
            "password_reset_invalid.html",
            {
                "message":
                    "This password reset link is invalid."
            }
        )

    except Exception:

        messages.error(
            request,
            "Unable to reset your password. "
            "Please try again."
        )

        return render(
            request,
            "reset_password.html",
            {
                "token": token
            }
        )

    # -----------------------------------------
    # Clear pending verification session
    # -----------------------------------------

    request.session.pop(
        "pending_verification_user_id",
        None
    )

    messages.success(
        request,
        "Your password has been changed successfully. "
        "You can now login."
    )

    return redirect(
        "login"
    )





from django.contrib.auth.decorators import login_required


# @login_required(login_url="login")
# def dashboard(request):
#     return render(request, "shop.html")


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import UserProfileForm
from .models import UserProfile



def validate_profile_image(image):

    allowed_types = [
        "image/jpeg",
        "image/png",
        "image/webp",
    ]

    max_size = 5 * 1024 * 1024

    if image.content_type not in allowed_types:
        return (
            False,
            "Only JPG, PNG, and WebP images are allowed."
        )

    if image.size > max_size:
        return (
            False,
            "Profile image must be smaller than 5 MB."
        )

    return True, None



# def user_profile(request):
#     return render(request, "user_profile.html")


from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# @login_required
# def user_profile(request):
#     user = request.user

#     context = {
#         "user": user,
#     }

#     return render(
#         request,
#         "user_profile.html",
#         context
#     )


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Address, Order


# @login_required
# def user_profile(request):

#     user = request.user

#     # ---------------------------------------------
#     # DEFAULT ADDRESS
#     # ---------------------------------------------

#     default_address = (
#         Address.objects
#         .filter(
#             user=user,
#             is_default=True
#         )
#         .first()
#     )

#     # ---------------------------------------------
#     # RECENT ORDERS
#     # ---------------------------------------------

#     recent_orders = (
#         Order.objects
#         .filter(user=user)
#         .order_by("-created_at")[:5]
#     )

#     # ---------------------------------------------
#     # RECENT ADDRESSES
#     # ---------------------------------------------

#     recent_addresses = (
#         Address.objects
#         .filter(user=user)
#         .order_by("-updated_at")[:5]
#     )

#     context = {
#         "user": user,
#         "default_address": default_address,
#         "recent_orders": recent_orders,
#         "recent_addresses": recent_addresses,
#     }

#     return render(
#         request,
#         "user_profile.html",
#         context
#     )




from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import (
    Address,
    Order,
    MilkSubscription,
)


@login_required
def user_profile(request):
    user = request.user

    default_address = (
        Address.objects
        .filter(
            user=user,
            is_default=True
        )
        .first()
    )

    recent_orders = (
        Order.objects
        .filter(user=user)
        .order_by("-created_at")[:5]
    )

    recent_addresses = (
        Address.objects
        .filter(user=user)
        .order_by("-updated_at")[:5]
    )

    # Active / pending / paused milk subscription
    subscription = (
        MilkSubscription.objects
        .filter(
            user=user,
            status__in=[
                "pending",
                "active",
                "paused",
            ],
        )
        .select_related("address")
        .prefetch_related(
            "items__product",
        )
        .first()
    )

    context = {
        "user": user,
        "default_address": default_address,
        "recent_orders": recent_orders,
        "recent_addresses": recent_addresses,
        "subscription": subscription,
    }

    return render(
        request,
        "user_profile.html",
        context
    )
    
    
@login_required(login_url="login")
@require_http_methods(["GET", "POST"])
def profile(request):

    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        form = UserProfileForm(
            request.POST,
            instance=profile
        )

        image = request.FILES.get("image")

        if form.is_valid():

            if image:

                is_valid, error_message = (
                    validate_profile_image(image)
                )

                if not is_valid:

                    messages.error(
                        request,
                        error_message
                    )

                else:

                    with transaction.atomic():

                        form.save()

                        request.user.address = (
                            request.POST.get(
                                "address",
                                ""
                            ).strip()
                        )

                        request.user.image = image

                        request.user.save(
                            update_fields=[
                                "address",
                                "image"
                            ]
                        )

                    messages.success(
                        request,
                        "Your profile has been updated successfully."
                    )

                    return redirect("profile")

            else:

                with transaction.atomic():

                    form.save()

                    request.user.address = (
                        request.POST.get(
                            "address",
                            ""
                        ).strip()
                    )

                    request.user.save(
                        update_fields=["address"]
                    )

                messages.success(
                    request,
                    "Your profile has been updated successfully."
                )

                return redirect("profile")

    else:

        form = UserProfileForm(
            instance=profile
        )

    context = {
        "form": form,
        "profile": profile,
        "completion_percentage": (
            profile.completion_percentage()
        ),
        "missing_fields": (
            profile.missing_fields()
        ),
    }

    return render(
        request,
        "profile.html",
        context
    )




from .models import (
    User,
    EmailVerificationToken,
    UserProfile,
    Category,
    Product,
)

# def shop(request):
#     categories = Category.objects.all().order_by("name")

#     products = (
#         Product.objects
#         .select_related("category")
#         .filter(is_active=True)
#         .order_by("-created_at")
#     )

#     context = {
#         "categories": categories,
#         "products": products,
#     }

#     return render(request, "shop.html", context)



def shop(request):
    """
    Customer-facing shop page.

    Displays:
    - Active categories
    - Featured active categories
    - Active products
    - Featured products
    - Products currently in stock
    """
    total_products=0
    categories = (
        Category.objects
        .filter(is_active=True)
        .order_by("name")
    )

    featured_categories = (
        Category.objects
        .filter(
            is_active=True,
            is_featured=True
        )
        .order_by("name")
    )

    products = (
        Product.objects
        .select_related("category")
        .filter(
            is_active=True
        )
        .order_by("-created_at")
    )

    featured_products = (
        Product.objects
        .select_related("category")
        .filter(
            is_active=True,
            is_featured=True
        )
        .order_by("-created_at")
    )

    in_stock_products = (
        Product.objects
        .select_related("category")
        .filter(
            is_active=True,
            is_in_stock=True
        )
        .order_by("-created_at")
    )
    total_products = products.count()
    # print("number of products==",total_products)

    context = {
        "categories": categories,
        "featured_categories": featured_categories,
        "products": products,
        "featured_products": featured_products,
        "in_stock_products": in_stock_products,
        "total_products": total_products,
    }

    return render(
        request,
        "shop.html",
        context
    )
    



from decimal import Decimal, InvalidOperation

from django.db.models import Q
from django.shortcuts import render

from .models import Category, Product


def shop_filter(request):
    """
    Combined product search, filtering and sorting.

    Supported filters:
    - Search
    - Category
    - Minimum price
    - Maximum price
    - In-stock
    - Featured
    - Sorting

    All results are returned to shop.html.
    """

    # ---------------------------------------------------------
    # Read GET parameters
    # ---------------------------------------------------------

    search_query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()

    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()

    stock_filter = request.GET.get("stock", "").strip()
    featured_filter = request.GET.get("featured", "").strip()

    sort = request.GET.get("sort", "newest").strip()

    # ---------------------------------------------------------
    # Base products
    # ---------------------------------------------------------

    products = (
        Product.objects
        .select_related("category")
        .filter(
            is_active=True
        )
    )

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    if search_query:

        products = products.filter(
            Q(name__icontains=search_query)
            | Q(short_description__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(sku__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )

    # ---------------------------------------------------------
    # Category
    # ---------------------------------------------------------

    selected_category_name = ""

    if category_slug:

        category = Category.objects.filter(
            slug=category_slug,
            is_active=True,
        ).first()

        if category:

            selected_category_name = category.name

            products = products.filter(
                category=category
            )

        else:

            category_slug = ""

    # ---------------------------------------------------------
    # Minimum Price
    # ---------------------------------------------------------

    if min_price:

        try:

            min_price_value = Decimal(min_price)

            if min_price_value >= 0:

                products = products.filter(
                    selling_price__gte=min_price_value
                )

            else:

                min_price = ""

        except (InvalidOperation, ValueError, TypeError):

            min_price = ""

    # ---------------------------------------------------------
    # Maximum Price
    # ---------------------------------------------------------

    if max_price:

        try:

            max_price_value = Decimal(max_price)

            if max_price_value >= 0:

                products = products.filter(
                    selling_price__lte=max_price_value
                )

            else:

                max_price = ""

        except (InvalidOperation, ValueError, TypeError):

            max_price = ""

    # ---------------------------------------------------------
    # Stock
    # ---------------------------------------------------------

    if stock_filter == "in_stock":

        products = products.filter(
            is_in_stock=True,
            stock_quantity__gt=0,
        )

    else:

        stock_filter = ""

    # ---------------------------------------------------------
    # Featured
    # ---------------------------------------------------------

    if featured_filter == "true":

        products = products.filter(
            is_featured=True
        )

    else:

        featured_filter = ""

    # ---------------------------------------------------------
    # Sorting
    # ---------------------------------------------------------

    sort_options = {

        "newest": "-created_at",

        "oldest": "created_at",

        "price_low": "selling_price",

        "price_high": "-selling_price",

        "name_az": "name",

        "name_za": "-name",

    }

    if sort not in sort_options:

        sort = "newest"

    products = products.order_by(
        sort_options[sort]
    )

    # ---------------------------------------------------------
    # Categories
    # ---------------------------------------------------------

    categories = (
        Category.objects
        .filter(is_active=True)
        .order_by("name")
    )

    featured_categories = (
        Category.objects
        .filter(
            is_active=True,
            is_featured=True,
        )
        .order_by("name")
    )

    # ---------------------------------------------------------
    # Existing shop sections
    # ---------------------------------------------------------

    featured_products = (
        Product.objects
        .select_related("category")
        .filter(
            is_active=True,
            is_featured=True,
        )
        .order_by("-created_at")
    )

    in_stock_products = (
        Product.objects
        .select_related("category")
        .filter(
            is_active=True,
            is_in_stock=True,
            stock_quantity__gt=0,
        )
        .order_by("-created_at")
    )

    # ---------------------------------------------------------
    # Result count
    # ---------------------------------------------------------

    total_products = products.count()

    # ---------------------------------------------------------
    # Context
    # ---------------------------------------------------------

    context = {

        "categories": categories,

        "featured_categories": featured_categories,

        # Filtered products
        "products": products,

        # Existing sections
        "featured_products": featured_products,

        "in_stock_products": in_stock_products,

        # Count
        "total_products": total_products,

        # Current filters
        "search_query": search_query,

        "selected_category": category_slug,

        "selected_category_name": selected_category_name,

        "min_price": min_price,

        "max_price": max_price,

        "stock_filter": stock_filter,

        "featured_filter": featured_filter,

        "selected_sort": sort,
    }

    return render(
        request,
        "shop.html",
        context
    )
    
    


# def product_detail(request, slug):
#     """
#     Display a single active product.

#     Product is looked up using its SEO-friendly slug.
#     """

#     product = (
#         Product.objects
#         .select_related("category")
#         .filter(
#             slug=slug,
#             is_active=True
#         )
#         .first()
#     )

#     if not product:
#         messages.error(
#             request,
#             "The product you are looking for is not available."
#         )
#         return redirect("shop")

#     context = {
#         "product": product,
#     }

#     return render(
#         request,
#         "product_detail.html",
#         context
#     )
    



def product_detail(request, slug):
    """
    Display a single active product along with similar products
    from the same category.
    """

    product = (
        Product.objects
        .select_related("category")
        .filter(
            slug=slug,
            is_active=True
        )
        .first()
    )

    if not product:
        messages.error(
            request,
            "The product you are looking for is not available."
        )
        return redirect("shop")

    # Similar products from the same category
    similar_products = (
        Product.objects
        .select_related("category")
        .filter(
            category=product.category,
            is_active=True,
        )
        .exclude(
            id=product.id
        )
        .order_by("-is_featured", "-created_at")[:8]
    )

    context = {
        "product": product,
        "similar_products": similar_products,
    }

    return render(
        request,
        "product_detail.html",
        context
    )



def category_products(request, slug):
    """
    Display products of a selected category
    using the existing shop.html template.
    """

    category = (
        Category.objects
        .filter(
            slug=slug,
            is_active=True
        )
        .first()
    )

    if not category:
        messages.error(
            request,
            "The category you are looking for is not available."
        )
        return redirect("shop")

    categories = (
        Category.objects
        .filter(is_active=True)
        .order_by("name")
    )

    featured_categories = (
        Category.objects
        .filter(
            is_active=True,
            is_featured=True
        )
        .order_by("name")
    )

    # Products only from selected category
    products = (
        Product.objects
        .select_related("category")
        .filter(
            category=category,
            is_active=True
        )
        .order_by("-created_at")
    )
    total_products=0
    total_products=products.count()

    # Featured products from selected category
    featured_products = (
        Product.objects
        .select_related("category")
        .filter(
            category=category,
            is_active=True,
            is_featured=True
        )
        .order_by("-created_at")
    )

    # In-stock products from selected category
    in_stock_products = (
        Product.objects
        .select_related("category")
        .filter(
            category=category,
            is_active=True,
            is_in_stock=True
        )
        .order_by("-created_at")
    )

    context = {
        "categories": categories,
        "featured_categories": featured_categories,

        "products": products,
        "featured_products": featured_products,
        "in_stock_products": in_stock_products,

        # Selected category
        "selected_category": category,
        "total_products":total_products,
    }

    return render(
        request,
        "shop.html",
        context
    )
    
    



# from django.views.decorators.http import require_POST

# @require_POST
# def cart_add(request, product_id):
#     """
#     Add a product to the session-based shopping cart.
#     """

#     # ---------------------------------
#     # Get active product
#     # ---------------------------------

#     product = (
#         Product.objects
#         .select_related("category")
#         .filter(
#             product_id=product_id,
#             is_active=True
#         )
#         .first()
#     )

#     if not product:
#         messages.error(
#             request,
#             "The product is no longer available."
#         )
#         return redirect("shop")


#     # ---------------------------------
#     # Check stock
#     # ---------------------------------

#     if not product.is_in_stock or product.stock_quantity <= 0:
#         messages.warning(
#             request,
#             f"{product.name} is currently out of stock."
#         )
#         return redirect(
#             "product-detail",
#             slug=product.slug
#         )


#     # ---------------------------------
#     # Get requested quantity
#     # ---------------------------------

#     try:
#         quantity = int(
#             request.POST.get("quantity", 1)
#         )
#     except (TypeError, ValueError):

#         messages.error(
#             request,
#             "Invalid quantity."
#         )

#         return redirect(
#             "product-detail",
#             slug=product.slug
#         )


#     # ---------------------------------
#     # Validate quantity
#     # ---------------------------------

#     if quantity < 1:

#         messages.error(
#             request,
#             "Quantity must be at least 1."
#         )

#         return redirect(
#             "product-detail",
#             slug=product.slug
#         )


#     # ---------------------------------
#     # Validate against stock
#     # ---------------------------------

#     if quantity > product.stock_quantity:

#         messages.warning(
#             request,
#             f"Only {product.stock_quantity} "
#             f"{product.get_unit_display()} available."
#         )

#         return redirect(
#             "product-detail",
#             slug=product.slug
#         )


#     # ---------------------------------
#     # Get existing cart
#     # ---------------------------------

#     cart = request.session.get("cart", {})


#     # ---------------------------------
#     # Product ID as string
#     # ---------------------------------

#     product_key = str(product.product_id)


#     # ---------------------------------
#     # Add / update quantity
#     # ---------------------------------

#     if product_key in cart:

#         existing_quantity = int(
#             cart[product_key]
#         )

#         new_quantity = (
#             existing_quantity + quantity
#         )

#         # Do not allow cart quantity
#         # to exceed available stock

#         if new_quantity > product.stock_quantity:

#             messages.warning(
#                 request,
#                 f"You can only add up to "
#                 f"{product.stock_quantity} "
#                 f"{product.get_unit_display()} "
#                 f"of {product.name}."
#             )

#             return redirect(
#                 "product-detail",
#                 slug=product.slug
#             )

#         cart[product_key] = new_quantity

#     else:

#         cart[product_key] = quantity


#     # ---------------------------------
#     # Save cart in session
#     # ---------------------------------

#     request.session["cart"] = cart

#     # Explicitly tell Django the session
#     # has been modified.

#     request.session.modified = True


#     # ---------------------------------
#     # Success message
#     # ---------------------------------

#     messages.success(
#         request,
#         f"{product.name} added to your cart."
#     )


#     # ---------------------------------
#     # Redirect
#     # ---------------------------------

#     return redirect("cart")










# def cart(request):
#     """
#     Display the current shopping cart.

#     Product prices are always fetched from the database.
#     Session data only stores product IDs and quantities.
#     """

#     session_cart = request.session.get("cart", {})

#     cart_items = []
#     subtotal = Decimal("0.00")

#     if session_cart:

#         product_ids = list(session_cart.keys())

#         products = (
#             Product.objects
#             .select_related("category")
#             .filter(
#                 product_id__in=product_ids,
#                 is_active=True
#             )
#         )

#         # Create a quick lookup dictionary
#         product_map = {
#             str(product.product_id): product
#             for product in products
#         }

#         cleaned_cart = {}

#         for product_id, quantity in session_cart.items():

#             product = product_map.get(str(product_id))

#             # Product no longer exists / inactive
#             if not product:
#                 continue

#             # Convert session quantity safely
#             try:
#                 quantity = int(quantity)
#             except (TypeError, ValueError):
#                 continue

#             if quantity < 1:
#                 continue

#             # Product currently out of stock
#             if (
#                 not product.is_in_stock
#                 or product.stock_quantity <= 0
#             ):
#                 continue

#             # Prevent old cart quantity from exceeding
#             # current available stock
#             if quantity > product.stock_quantity:
#                 quantity = int(product.stock_quantity)

#             if quantity < 1:
#                 continue

#             # Calculate item total using DB price
#             item_total = (
#                 product.selling_price
#                 * quantity
#             ).quantize(
#                 Decimal("0.01")
#             )

#             subtotal += item_total

#             cart_items.append({
#                 "product": product,
#                 "quantity": quantity,
#                 "item_total": item_total,
#             })

#             cleaned_cart[str(product.product_id)] = quantity

#         # Keep session cart clean
#         if cleaned_cart != session_cart:
#             request.session["cart"] = cleaned_cart
#             request.session.modified = True

#     context = {
#         "cart_items": cart_items,
#         "subtotal": subtotal,
#         "cart_count": sum(
#             item["quantity"]
#             for item in cart_items
#         ),
#     }

#     return render(
#         request,
#         "cart.html",
#         context
#     )
    



# @require_POST
# def cart_update(request, product_id):
#     product = (
#         Product.objects
#         .select_related("category")
#         .filter(product_id=product_id, is_active=True)
#         .first()
#     )

#     if not product:
#         messages.error(request, "The product is no longer available.")
#         return redirect("cart")

#     if not product.is_in_stock or product.stock_quantity <= 0:
#         messages.warning(
#             request,
#             f"{product.name} is currently out of stock."
#         )

#         cart = request.session.get("cart", {})
#         cart.pop(str(product_id), None)

#         request.session["cart"] = cart
#         request.session.modified = True

#         return redirect("cart")

#     try:
#         quantity = int(request.POST.get("quantity", 1))
#     except (TypeError, ValueError):
#         messages.error(request, "Invalid quantity.")
#         return redirect("cart")

#     if quantity < 1:
#         messages.error(request, "Quantity must be at least 1.")
#         return redirect("cart")

#     if quantity > product.stock_quantity:
#         messages.warning(
#             request,
#             f"Only {product.stock_quantity} "
#             f"{product.get_unit_display()} of {product.name} are available."
#         )
#         return redirect("cart")

#     cart = request.session.get("cart", {})
#     product_key = str(product.product_id)

#     if product_key not in cart:
#         messages.error(request, "This product is not in your cart.")
#         return redirect("cart")

#     cart[product_key] = quantity

#     request.session["cart"] = cart
#     request.session.modified = True

#     messages.success(
#         request,
#         f"{product.name} quantity updated."
#     )

#     return redirect("cart")


# @require_POST
# def cart_remove(request, product_id):
#     cart = request.session.get("cart", {})
#     product_key = str(product_id)

#     if product_key in cart:
#         cart.pop(product_key)

#         request.session["cart"] = cart
#         request.session.modified = True

#         messages.success(
#             request,
#             "Product removed from your cart."
#         )
#     else:
#         messages.warning(
#             request,
#             "This product is not in your cart."
#         )

#     return redirect("cart")







    

from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
@require_POST
def cart_add(request, product_id):

    product = (
        Product.objects
        .select_related("category")
        .filter(
            product_id=product_id,
            is_active=True
        )
        .first()
    )

    if not product:
        messages.error(
            request,
            "The product is no longer available."
        )
        return redirect("shop")

    if (
        not product.is_in_stock
        or product.stock_quantity <= 0
    ):
        messages.warning(
            request,
            f"{product.name} is currently out of stock."
        )
        return redirect(
            "product-detail",
            slug=product.slug
        )

    try:
        quantity = int(
            request.POST.get("quantity", 1)
        )
        next_url = request.POST.get("next", "")

        if not url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = ""
    except (TypeError, ValueError):

        messages.error(
            request,
            "Invalid quantity."
        )

        return redirect(
            "product-detail",
            slug=product.slug
        )

    if quantity < 1:

        messages.error(
            request,
            "Quantity must be at least 1."
        )

        return redirect(
            "product-detail",
            slug=product.slug
        )

    if quantity > product.stock_quantity:

        messages.warning(
            request,
            f"Only {product.stock_quantity} "
            f"{product.get_unit_display()} available."
        )

        return redirect(
            "product-detail",
            slug=product.slug
        )

    # -------------------------------------------------
    # LOGGED-IN USER
    # -------------------------------------------------

    if request.user.is_authenticated:

        with transaction.atomic():

            cart, created = Cart.objects.get_or_create(
                user=request.user
            )

            cart_item = (
                CartItem.objects
                .filter(
                    cart=cart,
                    product=product
                )
                .first()
            )

            if cart_item:

                new_quantity = (
                    cart_item.quantity + quantity
                )

                if new_quantity > product.stock_quantity:

                    messages.warning(
                        request,
                        f"You can only add up to "
                        f"{product.stock_quantity} "
                        f"{product.get_unit_display()} "
                        f"of {product.name}."
                    )

                    return redirect(
                        "product-detail",
                        slug=product.slug
                    )

                cart_item.quantity = new_quantity

                cart_item.save(
                    update_fields=[
                        "quantity",
                        "updated_at"
                    ]
                )

            else:

                CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=quantity
                )

    # -------------------------------------------------
    # GUEST USER
    # -------------------------------------------------

    else:

        cart = request.session.get(
            "cart",
            {}
        )

        product_key = str(
            product.product_id
        )

        existing_quantity = int(
            cart.get(product_key, 0)
        )

        new_quantity = (
            existing_quantity + quantity
        )

        if new_quantity > product.stock_quantity:

            messages.warning(
                request,
                f"You can only add up to "
                f"{product.stock_quantity} "
                f"{product.get_unit_display()} "
                f"of {product.name}."
            )

            return redirect(
                "product-detail",
                slug=product.slug
            )

        cart[product_key] = new_quantity

        request.session["cart"] = cart
        request.session.modified = True
        
    
    messages.success(
    request,
    f"{product.name} added to your cart."
)

    if next_url:
        return redirect(next_url)

    return redirect("cart")

    # messages.success(
    #     request,
    #     f"{product.name} added to your cart."
    # )

    # return redirect("cart")




def cart(request):

    # =================================================
    # LOGGED-IN USER
    # =================================================

    if request.user.is_authenticated:

        # First merge any guest cart
        merge_session_cart_to_database(request)

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        cart_items = (
            cart.items
            .select_related(
                "product",
                "product__category"
            )
            .filter(
                product__is_active=True
            )
        )

        valid_items = []
        subtotal = Decimal("0.00")

        for item in cart_items:

            product = item.product

            if (
                not product.is_in_stock
                or product.stock_quantity <= 0
            ):
                item.delete()
                continue

            if item.quantity > product.stock_quantity:

                item.quantity = int(
                    product.stock_quantity
                )

                if item.quantity <= 0:
                    item.delete()
                    continue

                item.save(
                    update_fields=[
                        "quantity",
                        "updated_at"
                    ]
                )

            item_total = item.item_total

            subtotal += item_total

            valid_items.append({
                "product": product,
                "quantity": item.quantity,
                "item_total": item_total,
                "cart_item": item,
            })

    # =================================================
    # GUEST USER
    # =================================================

    else:

        session_cart = request.session.get(
            "cart",
            {}
        )

        valid_items = []
        subtotal = Decimal("0.00")

        if session_cart:

            product_ids = list(
                session_cart.keys()
            )

            products = (
                Product.objects
                .select_related("category")
                .filter(
                    product_id__in=product_ids,
                    is_active=True
                )
            )

            product_map = {
                str(product.product_id): product
                for product in products
            }

            cleaned_cart = {}

            for product_id, quantity in session_cart.items():

                product = product_map.get(
                    str(product_id)
                )

                if not product:
                    continue

                if (
                    not product.is_in_stock
                    or product.stock_quantity <= 0
                ):
                    continue

                try:
                    quantity = int(quantity)
                except (TypeError, ValueError):
                    continue

                if quantity < 1:
                    continue

                if quantity > product.stock_quantity:
                    quantity = int(
                        product.stock_quantity
                    )

                if quantity < 1:
                    continue

                item_total = (
                    product.selling_price * quantity
                ).quantize(
                    Decimal("0.01")
                )

                subtotal += item_total

                valid_items.append({
                    "product": product,
                    "quantity": quantity,
                    "item_total": item_total,
                    "cart_item": None,
                })

                cleaned_cart[
                    str(product.product_id)
                ] = quantity

            if cleaned_cart != session_cart:

                request.session["cart"] = cleaned_cart
                request.session.modified = True

    context = {
        "cart_items": valid_items,
        "subtotal": subtotal.quantize(
            Decimal("0.01")
        ),
        "cart_count": sum(
            item["quantity"]
            for item in valid_items
        ),
    }

    return render(
        request,
        "cart.html",
        context
    )
    
    
    



@require_POST
def cart_update(request, product_id):

    try:
        quantity = int(
            request.POST.get("quantity", 1)
        )
    except (TypeError, ValueError):

        messages.error(
            request,
            "Invalid quantity."
        )

        return redirect("cart")

    if quantity < 1:

        messages.error(
            request,
            "Quantity must be at least 1."
        )

        return redirect("cart")

    product = (
        Product.objects
        .filter(
            product_id=product_id,
            is_active=True
        )
        .first()
    )

    if not product:

        messages.error(
            request,
            "The product is no longer available."
        )

        return redirect("cart")

    if (
        not product.is_in_stock
        or product.stock_quantity <= 0
    ):

        messages.warning(
            request,
            f"{product.name} is currently out of stock."
        )

        return redirect("cart")

    if quantity > product.stock_quantity:

        messages.warning(
            request,
            f"Only {product.stock_quantity} "
            f"{product.get_unit_display()} available."
        )

        return redirect("cart")

    # =================================================
    # LOGGED-IN USER
    # =================================================

    if request.user.is_authenticated:

        merge_session_cart_to_database(request)

        cart = (
            Cart.objects
            .filter(user=request.user)
            .first()
        )

        if not cart:

            messages.error(
                request,
                "Your cart is empty."
            )

            return redirect("cart")

        cart_item = (
            CartItem.objects
            .filter(
                cart=cart,
                product=product
            )
            .first()
        )

        if not cart_item:

            messages.error(
                request,
                "This product is not in your cart."
            )

            return redirect("cart")

        cart_item.quantity = quantity

        cart_item.save(
            update_fields=[
                "quantity",
                "updated_at"
            ]
        )

    # =================================================
    # GUEST USER
    # =================================================

    else:

        cart = request.session.get(
            "cart",
            {}
        )

        product_key = str(product.product_id)

        if product_key not in cart:

            messages.error(
                request,
                "This product is not in your cart."
            )

            return redirect("cart")

        cart[product_key] = quantity

        request.session["cart"] = cart
        request.session.modified = True

    messages.success(
        request,
        f"{product.name} quantity updated."
    )

    return redirect("cart")





@require_POST
def cart_remove(request, product_id):

    product_key = str(product_id)

    # =================================================
    # LOGGED-IN USER
    # =================================================

    if request.user.is_authenticated:

        merge_session_cart_to_database(request)

        cart = (
            Cart.objects
            .filter(user=request.user)
            .first()
        )

        if cart:

            deleted_count, _ = (
                CartItem.objects
                .filter(
                    cart=cart,
                    product__product_id=product_key
                )
                .delete()
            )

            if deleted_count:

                messages.success(
                    request,
                    "Product removed from your cart."
                )

            else:

                messages.warning(
                    request,
                    "This product is not in your cart."
                )

    # =================================================
    # GUEST USER
    # =================================================

    else:

        cart = request.session.get(
            "cart",
            {}
        )

        if product_key in cart:

            cart.pop(product_key)

            request.session["cart"] = cart
            request.session.modified = True

            messages.success(
                request,
                "Product removed from your cart."
            )

        else:

            messages.warning(
                request,
                "This product is not in your cart."
            )

    return redirect("cart")







@login_required
@require_http_methods(["GET", "POST"])
def address_add(request):
    next_url = request.GET.get("next") or request.POST.get("next")

    if not next_url:
        next_url = "addresses"

    if request.method == "POST":

        full_name = request.POST.get(
            "full_name", ""
        ).strip()

        phone_number = request.POST.get(
            "phone_number", ""
        ).strip()

        address_line1 = request.POST.get(
            "address_line1", ""
        ).strip()

        address_line2 = request.POST.get(
            "address_line2", ""
        ).strip()

        landmark = request.POST.get(
            "landmark", ""
        ).strip()

        city = request.POST.get(
            "city", ""
        ).strip()

        state = request.POST.get(
            "state", ""
        ).strip()

        pincode = request.POST.get(
            "pincode", ""
        ).strip()

        address_type = request.POST.get(
            "address_type", "home"
        ).strip()

        is_default = (
            request.POST.get("is_default")
            == "on"
        )

        # -----------------------------
        # Validation
        # -----------------------------

        if not full_name:
            messages.error(
                request,
                "Full name is required."
            )
            return redirect("address-add")

        if not phone_number:
            messages.error(
                request,
                "Phone number is required."
            )
            return redirect("address-add")

        if not re.fullmatch(
            r"\+?[0-9]{10,15}",
            phone_number
        ):
            messages.error(
                request,
                "Enter a valid phone number."
            )
            return redirect("address-add")

        if not address_line1:
            messages.error(
                request,
                "Address is required."
            )
            return redirect("address-add")

        if not city:
            messages.error(
                request,
                "City is required."
            )
            return redirect("address-add")

        if not state:
            messages.error(
                request,
                "State is required."
            )
            return redirect("address-add")

        if not re.fullmatch(
            r"[0-9]{6}",
            pincode
        ):
            messages.error(
                request,
                "Enter a valid 6-digit pincode."
            )
            return redirect("address-add")

        if address_type not in {
            "home",
            "work",
            "other"
        }:
            messages.error(
                request,
                "Invalid address type."
            )
            return redirect("address-add")

        # -----------------------------
        # Default address handling
        # -----------------------------

        with transaction.atomic():

            if is_default:

                Address.objects.filter(
                    user=request.user,
                    is_default=True
                ).update(
                    is_default=False
                )

            address = Address.objects.create(
                user=request.user,
                full_name=full_name,
                phone_number=phone_number,
                address_line1=address_line1,
                address_line2=address_line2,
                landmark=landmark,
                city=city,
                state=state,
                pincode=pincode,
                address_type=address_type,
                is_default=is_default
            )

            # If this is the user's first address,
            # automatically make it default.
            if not Address.objects.filter(
                user=request.user
            ).exclude(
                pk=address.pk
            ).exists():

                address.is_default = True
                address.save(
                    update_fields=[
                        "is_default",
                        "updated_at"
                    ]
                )
                
        
        # Securely validate return URL
        if url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        
        messages.success(
                    request,
                    "Address added successfully."
                )

        return redirect("addresses")

        # messages.success(
        #     request,
        #     "Address added successfully."
        # )
# 
        # return redirect("addresses")

    return render(
         request,
        "address_add.html",
        {
            "next_url": next_url,
        },
       
    )
    
    




@login_required
def address_list(request):

    addresses = (
        Address.objects
        .filter(user=request.user)
        .order_by(
            "-is_default",
            "-created_at"
        )
    )

    return render(
        request,
        "address_list.html",
        {
            "addresses": addresses
        }
    )
    
    
    
    

@login_required
@require_http_methods(["GET", "POST"])
def address_edit(request, address_id):

    address = (
        Address.objects
        .filter(
            id=address_id,
            user=request.user
        )
        .first()
    )

    if not address:

        messages.error(
            request,
            "Address not found."
        )

        return redirect("addresses")

    if request.method == "POST":

        full_name = request.POST.get(
            "full_name", ""
        ).strip()

        phone_number = request.POST.get(
            "phone_number", ""
        ).strip()

        address_line1 = request.POST.get(
            "address_line1", ""
        ).strip()

        address_line2 = request.POST.get(
            "address_line2", ""
        ).strip()

        landmark = request.POST.get(
            "landmark", ""
        ).strip()

        city = request.POST.get(
            "city", ""
        ).strip()

        state = request.POST.get(
            "state", ""
        ).strip()

        pincode = request.POST.get(
            "pincode", ""
        ).strip()

        address_type = request.POST.get(
            "address_type",
            "home"
        ).strip()

        is_default = (
            request.POST.get("is_default")
            == "on"
        )

        # -----------------------------
        # Validation
        # -----------------------------

        if not full_name:
            messages.error(
                request,
                "Full name is required."
            )
            return redirect(
                "address-edit",
                address_id=address.id
            )

        if not re.fullmatch(
            r"\+?[0-9]{10,15}",
            phone_number
        ):
            messages.error(
                request,
                "Enter a valid phone number."
            )
            return redirect(
                "address-edit",
                address_id=address.id
            )

        if not address_line1:
            messages.error(
                request,
                "Address is required."
            )
            return redirect(
                "address-edit",
                address_id=address.id
            )

        if not city:
            messages.error(
                request,
                "City is required."
            )
            return redirect(
                "address-edit",
                address_id=address.id
            )

        if not state:
            messages.error(
                request,
                "State is required."
            )
            return redirect(
                "address-edit",
                address_id=address.id
            )

        if not re.fullmatch(
            r"[0-9]{6}",
            pincode
        ):
            messages.error(
                request,
                "Enter a valid 6-digit pincode."
            )
            return redirect(
                "address-edit",
                address_id=address.id
            )

        if address_type not in {
            "home",
            "work",
            "other"
        }:
            messages.error(
                request,
                "Invalid address type."
            )
            return redirect(
                "address-edit",
                address_id=address.id
            )

        with transaction.atomic():

            if is_default:

                Address.objects.filter(
                    user=request.user,
                    is_default=True
                ).exclude(
                    id=address.id
                ).update(
                    is_default=False
                )

            address.full_name = full_name
            address.phone_number = phone_number
            address.address_line1 = address_line1
            address.address_line2 = address_line2
            address.landmark = landmark
            address.city = city
            address.state = state
            address.pincode = pincode
            address.address_type = address_type
            address.is_default = is_default

            address.save()

        messages.success(
            request,
            "Address updated successfully."
        )

        return redirect("addresses")

    return render(
        request,
        "address_edit.html",
        {
            "address": address
        }
    )
    
    
    



@login_required
@require_POST
def address_delete(request, address_id):

    address = (
        Address.objects
        .filter(
            id=address_id,
            user=request.user
        )
        .first()
    )

    if not address:

        messages.error(
            request,
            "Address not found."
        )

        return redirect("addresses")

    was_default = address.is_default

    with transaction.atomic():

        address.delete()

        # If deleted address was default,
        # choose another address as default.
        if was_default:

            next_address = (
                Address.objects
                .filter(
                    user=request.user
                )
                .order_by(
                    "-created_at"
                )
                .first()
            )

            if next_address:

                next_address.is_default = True

                next_address.save(
                    update_fields=[
                        "is_default",
                        "updated_at"
                    ]
                )

    messages.success(
        request,
        "Address deleted successfully."
    )

    return redirect("addresses")






@login_required
@require_POST
@transaction.atomic
def address_set_default(
    request,
    address_id
):

    address = (
        Address.objects
        .filter(
            id=address_id,
            user=request.user
        )
        .first()
    )

    if not address:

        messages.error(
            request,
            "Address not found."
        )

        return redirect("addresses")

    Address.objects.filter(
        user=request.user,
        is_default=True
    ).exclude(
        id=address.id
    ).update(
        is_default=False
    )

    address.is_default = True

    address.save(
        update_fields=[
            "is_default",
            "updated_at"
        ]
    )

    messages.success(
        request,
        "Default address updated."
    )

    return redirect("addresses")









@login_required
def checkout(request):

    cart = (
        Cart.objects
        .filter(user=request.user)
        .first()
    )

    if not cart:
        messages.warning(
            request,
            "Your cart is empty."
        )
        return redirect("cart")

    cart_items = (
        cart.items
        .select_related(
            "product",
            "product__category"
        )
        .filter(
            product__is_active=True
        )
    )

    if not cart_items.exists():

        messages.warning(
            request,
            "Your cart is empty."
        )

        return redirect("cart")

    valid_items = []
    subtotal = Decimal("0.00")

    for item in cart_items:

        product = item.product

        # Product unavailable
        if (
            not product.is_in_stock
            or product.stock_quantity <= 0
        ):
            messages.warning(
                request,
                f"{product.name} is no longer available."
            )
            continue

        # Current stock lower than cart quantity
        if item.quantity > product.stock_quantity:

            item.quantity = int(
                product.stock_quantity
            )

            if item.quantity <= 0:
                item.delete()
                continue

            item.save(
                update_fields=[
                    "quantity",
                    "updated_at"
                ]
            )

        item_total = (
            product.selling_price * item.quantity
        ).quantize(
            Decimal("0.01")
        )

        subtotal += item_total

        valid_items.append({
            "cart_item": item,
            "product": product,
            "quantity": item.quantity,
            "item_total": item_total,
        })

    if not valid_items:

        messages.warning(
            request,
            "There are no available products in your cart."
        )

        return redirect("cart")

    addresses = (
        Address.objects
        .filter(
            user=request.user
        )
        .order_by(
            "-is_default",
            "-created_at"
        )
    )

    if not addresses.exists():

        messages.info(
            request,
            "Please add a delivery address first."
        )

        return redirect("address-add")

    default_address = addresses.filter(
        is_default=True
    ).first()

    if not default_address:
        default_address = addresses.first()

    delivery_charge = Decimal("0.00")

    total_amount = (
        subtotal + delivery_charge
    ).quantize(
        Decimal("0.01")
    )
    
    
    checkout_token = request.session.get("checkout_token")

    if not checkout_token:
        checkout_token = uuid.uuid4().hex

        request.session["checkout_token"] = checkout_token
        request.session.modified = True
    # checkout_token = uuid.uuid4().hex

    # request.session["checkout_token"] = checkout_token
    # request.session.modified = True

    context = {
        "cart_items": valid_items,
        "addresses": addresses,
        "default_address": default_address,
        "subtotal": subtotal.quantize(
            Decimal("0.01")
        ),
        "delivery_charge": delivery_charge,
        "total_amount": total_amount,
        "checkout_token": checkout_token,
    }

    return render(
        request,
        "checkout.html",
        context
    )
    
    
    


from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .models import (
    Address,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Product,
)


# @login_required
# def place_order(request):

#     if request.method != "POST":
#         return redirect("checkout")

#     selected_address_id = request.POST.get("selected_address")
#     payment_method = request.POST.get("payment_method")

#     # --------------------------------------------------
#     # Basic validation
#     # --------------------------------------------------

#     if not selected_address_id:
#         messages.error(
#             request,
#             "Please select a delivery address."
#         )
#         return redirect("checkout")

#     allowed_payment_methods = {
#         choice[0]
#         for choice in Order.PAYMENT_METHOD_CHOICES
#     }

#     if payment_method not in allowed_payment_methods:
#         messages.error(
#             request,
#             "Invalid payment method."
#         )
#         return redirect("checkout")

#     # --------------------------------------------------
#     # Get address belonging to current user
#     # --------------------------------------------------

#     address = (
#         Address.objects
#         .filter(
#             id=selected_address_id,
#             user=request.user
#         )
#         .first()
#     )

#     if not address:
#         messages.error(
#             request,
#             "The selected address is invalid."
#         )
#         return redirect("checkout")

#     # --------------------------------------------------
#     # Atomic order creation
#     # --------------------------------------------------

#     try:

#         with transaction.atomic():

#             # ------------------------------------------
#             # Get user's cart
#             # ------------------------------------------

#             cart = (
#                 Cart.objects
#                 .select_for_update()
#                 .filter(user=request.user)
#                 .first()
#             )

#             if not cart:
#                 messages.error(
#                     request,
#                     "Your cart is empty."
#                 )
#                 return redirect("cart")

#             # ------------------------------------------
#             # Get cart items
#             # ------------------------------------------

#             cart_items = list(
#                 CartItem.objects
#                 .filter(cart=cart)
#                 .select_related("product")
#             )

#             if not cart_items:
#                 messages.error(
#                     request,
#                     "Your cart is empty."
#                 )
#                 return redirect("cart")

#             # ------------------------------------------
#             # Lock products
#             # ------------------------------------------

#             product_ids = [
#                 item.product_id
#                 for item in cart_items
#             ]

#             locked_products = {
#                 product.id: product
#                 for product in (
#                     Product.objects
#                     .select_for_update()
#                     .filter(id__in=product_ids)
#                 )
#             }

#             subtotal = Decimal("0.00")

#             validated_items = []

#             # ------------------------------------------
#             # Validate every cart item
#             # ------------------------------------------

#             for cart_item in cart_items:

#                 product = locked_products.get(
#                     cart_item.product_id
#                 )

#                 if not product:
#                     raise ValueError(
#                         "A product in your cart no longer exists."
#                     )

#                 # --------------------------------------
#                 # Product availability
#                 # --------------------------------------

#                 if not product.is_active:
#                     raise ValueError(
#                         f"{product.name} is no longer available."
#                     )

#                 if not product.is_in_stock:
#                     raise ValueError(
#                         f"{product.name} is currently out of stock."
#                     )

#                 # --------------------------------------
#                 # Stock validation
#                 # --------------------------------------

#                 if product.stock_quantity <= 0:
#                     raise ValueError(
#                         f"{product.name} is currently out of stock."
#                     )

#                 if cart_item.quantity > product.stock_quantity:
#                     raise ValueError(
#                         f"Only {product.stock_quantity} "
#                         f"{product.unit} of {product.name} "
#                         f"is available."
#                     )

#                 # --------------------------------------
#                 # Recalculate price from DB
#                 # --------------------------------------

#                 unit_price = (
#                     product.selling_price
#                 ).quantize(
#                     Decimal("0.01")
#                 )

#                 item_total = (
#                     unit_price * cart_item.quantity
#                 ).quantize(
#                     Decimal("0.01")
#                 )

#                 subtotal += item_total

#                 validated_items.append({
#                     "product": product,
#                     "quantity": cart_item.quantity,
#                     "unit_price": unit_price,
#                     "discount_percentage": (
#                         product.discount_percentage
#                     ),
#                     "total_price": item_total,
#                 })

#             # ------------------------------------------
#             # Delivery charge
#             # ------------------------------------------

#             delivery_charge = Decimal("0.00")

#             # ------------------------------------------
#             # Final total
#             # ------------------------------------------

#             total_amount = (
#                 subtotal + delivery_charge
#             ).quantize(
#                 Decimal("0.01")
#             )

#             # ------------------------------------------
#             # Payment status
#             # ------------------------------------------

#             if payment_method == "cod":
#                 payment_status = "pending"

#             else:
#                 # Razorpay will be implemented next.
#                 payment_status = "pending"

#             # ------------------------------------------
#             # Create Order
#             # ------------------------------------------

#             order = Order.objects.create(
#                 user=request.user,

#                 # Address snapshot
#                 full_name=address.full_name,
#                 phone_number=address.phone_number,
#                 address_line1=address.address_line1,
#                 address_line2=address.address_line2,
#                 landmark=address.landmark,
#                 city=address.city,
#                 state=address.state,
#                 pincode=address.pincode,

#                 # Amounts
#                 subtotal=subtotal,
#                 delivery_charge=delivery_charge,
#                 total_amount=total_amount,

#                 # Payment
#                 payment_method=payment_method,
#                 payment_status=payment_status,

#                 # Order status
#                 status="pending",
#             )

#             # ------------------------------------------
#             # Create Order Items + Reduce Stock
#             # ------------------------------------------

#             for item in validated_items:

#                 product = item["product"]

#                 OrderItem.objects.create(
#                     order=order,
#                     product=product,

#                     # Product snapshot
#                     product_name=product.name,
#                     sku=product.sku,
#                     unit=product.unit,

#                     quantity=item["quantity"],

#                     unit_price=item["unit_price"],

#                     discount_percentage=(
#                         item["discount_percentage"]
#                     ),

#                     total_price=item["total_price"],
#                 )

#                 # --------------------------------------
#                 # Reduce stock
#                 # --------------------------------------

#                 product.stock_quantity -= item["quantity"]

#                 # Update stock availability
#                 product.is_in_stock = (
#                     product.stock_quantity > 0
#                 )

#                 product.save(
#                     update_fields=[
#                         "stock_quantity",
#                         "is_in_stock",
#                         "updated_at",
#                     ]
#                 )

#             # ------------------------------------------
#             # Clear cart
#             # ------------------------------------------

#             CartItem.objects.filter(
#                 cart=cart
#             ).delete()

#         # --------------------------------------------------
#         # Order successfully created
#         # --------------------------------------------------

#         messages.success(
#             request,
#             f"Order {order.order_number} placed successfully."
#         )

#         return redirect(
#             "order-success",
#             order_number=order.order_number
#         )

#     except ValueError as e:

#         messages.error(
#             request,
#             str(e)
#         )

#         return redirect("checkout")

#     except Exception:

#         messages.error(
#             request,
#             "Something went wrong while placing your order. "
#             "Please try again."
#         )

#         return redirect("checkout")
    



def send_order_confirmation_emails(order_id):
    """
    Send:
    1. Order confirmation to customer
    2. New order notification to admin
    """

    try:
        order = (
            Order.objects
            .select_related("user")
            .prefetch_related("items__product")
            .get(pk=order_id)
        )

        # --------------------------------------------------
        # ORDER DETAILS LINK
        # --------------------------------------------------

        order_path = reverse(
            "order-success",
            kwargs={
                "order_number": order.order_number
            }
        )

        order_url = (
            f"{settings.SITE_URL}"
            f"{order_path}"
        )

        # --------------------------------------------------
        # CUSTOMER ITEMS
        # --------------------------------------------------

        customer_items = ""

        for item in order.items.all():
            customer_items += (
                f"{item.product_name} "
                f"x {item.quantity} "
                f"- ₹{item.total_price:.2f}\n"
            )

#         # --------------------------------------------------
#         # CUSTOMER EMAIL
#         # --------------------------------------------------

#         customer_subject = (
#             f"Order Confirmed - {order.order_number}"
#         )

#         customer_message = f"""
# Hello {order.user.full_name},

# Thank you for ordering from Rajanna Dairy Farm!

# Your order has been successfully placed.

# ORDER DETAILS
# ------------------------------
# Order Number: {order.order_number}

# Items:
# {customer_items}

# Subtotal: ₹{order.subtotal:.2f}
# Delivery Charge: ₹{order.delivery_charge:.2f}
# Total Amount: ₹{order.total_amount:.2f}

# Payment Method: {order.get_payment_method_display()}
# Payment Status: {order.get_payment_status_display()}
# Order Status: {order.get_status_display()}

# DELIVERY ADDRESS
# ------------------------------
# {order.full_name}
# {order.address_line1}
# {order.address_line2 or ""}
# {order.landmark or ""}
# {order.city}, {order.state} - {order.pincode}
# Phone: {order.phone_number}

# View your order:
# {order_url}

# Thank you for choosing Rajanna Dairy Farm.

# Regards,
# Rajanna Dairy Farm
# """

#         customer_email = EmailMultiAlternatives(
#             subject=customer_subject,
#             body=customer_message,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=[order.user.email],
#         )

#         customer_email.send(
#             fail_silently=False
#         )

#         # --------------------------------------------------
#         # ADMIN EMAIL
#         # --------------------------------------------------

#         admin_subject = (
#             f"🛒 New Order Received - "
#             f"{order.order_number}"
#         )

#         admin_message = f"""
# NEW ORDER RECEIVED
# ==============================

# Order Number:
# {order.order_number}

# CUSTOMER
# ------------------------------
# Name: {order.user.full_name}
# Email: {order.user.email}
# Phone: {order.phone_number}

# ORDER ITEMS
# ------------------------------
# {customer_items}

# ORDER AMOUNT
# ------------------------------
# Subtotal: ₹{order.subtotal:.2f}
# Delivery Charge: ₹{order.delivery_charge:.2f}
# Total: ₹{order.total_amount:.2f}

# PAYMENT
# ------------------------------
# Method: {order.get_payment_method_display()}
# Status: {order.get_payment_status_display()}

# ORDER STATUS
# ------------------------------
# {order.get_status_display()}

# DELIVERY ADDRESS
# ------------------------------
# {order.full_name}
# {order.address_line1}
# {order.address_line2 or ""}
# {order.landmark or ""}
# {order.city}, {order.state} - {order.pincode}

# Phone: {order.phone_number}

# Please check the Django admin panel
# for complete order information.

# Rajanna Dairy Farm
# """

#         admin_email = EmailMultiAlternatives(
#             subject=admin_subject,
#             body=admin_message,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=[settings.ADMIN_EMAIL],
#         )

#         admin_email.send(
#             fail_silently=False
#         )



        # --------------------------------------------------
        # CUSTOMER EMAIL
        # --------------------------------------------------
        customer_subject = f"Order Confirmed - {order.order_number}"

        customer_text = f"""
        Hello {order.user.full_name},

        Thank you for ordering from Rajanna Dairy Farm!

        Your order has been successfully placed.

        ORDER DETAILS
        ------------------------------
        Order Number: {order.order_number}

        Items:
        {customer_items}

        Subtotal: ₹{order.subtotal:.2f}
        Delivery Charge: ₹{order.delivery_charge:.2f}
        Total Amount: ₹{order.total_amount:.2f}

        Payment Method: {order.get_payment_method_display()}
        Payment Status: {order.get_payment_status_display()}
        Order Status: {order.get_status_display()}

        DELIVERY ADDRESS
        ------------------------------
        {order.full_name}
        {order.address_line1}
        {order.address_line2 or ""}
        {order.landmark or ""}
        {order.city}, {order.state} - {order.pincode}
        Phone: {order.phone_number}

        View your order:
        {order_url}

        Thank you for choosing Rajanna Dairy Farm.

        Regards,
        Rajanna Dairy Farm
        """

        customer_html = f"""
        <p>Hello {order.user.full_name},</p>
        <p>Thank you for ordering from <strong>Rajanna Dairy Farm</strong>!</p>
        <p>Your order has been successfully placed.</p>

        <h3>Order Details</h3>
        <ul>
        <li><strong>Order Number:</strong> {order.order_number}</li>
        <li><strong>Items:</strong><br>{customer_items}</li>
        <li><strong>Subtotal:</strong> ₹{order.subtotal:.2f}</li>
        <li><strong>Delivery Charge:</strong> ₹{order.delivery_charge:.2f}</li>
        <li><strong>Total Amount:</strong> ₹{order.total_amount:.2f}</li>
        <li><strong>Payment Method:</strong> {order.get_payment_method_display()}</li>
        <li><strong>Payment Status:</strong> {order.get_payment_status_display()}</li>
        <li><strong>Order Status:</strong> {order.get_status_display()}</li>
        </ul>

        <h3>Delivery Address</h3>
        <p>
        {order.full_name}<br>
        {order.address_line1}<br>
        {order.address_line2 or ""}<br>
        {order.landmark or ""}<br>
        {order.city}, {order.state} - {order.pincode}<br>
        Phone: {order.phone_number}
        </p>

        <p><a href="{order_url}">View your order</a></p>

        <p>Thank you for choosing Rajanna Dairy Farm.</p>
        <p>Regards,<br>Rajanna Dairy Farm</p>
        """

        resend.Emails.send({
            "from": "Rajanna Dairy Farm <onboarding@resend.dev>",
            "to": [order.user.email],
            "subject": customer_subject,
            "text": customer_text,
            "html": customer_html,
        })

        # --------------------------------------------------
        # ADMIN EMAIL
        # --------------------------------------------------
        admin_subject = f"🛒 New Order Received - {order.order_number}"

        admin_text = f"""
        NEW ORDER RECEIVED
        ==============================

        Order Number: {order.order_number}

        CUSTOMER
        ------------------------------
        Name: {order.user.full_name}
        Email: {order.user.email}
        Phone: {order.phone_number}

        ORDER ITEMS
        ------------------------------
        {customer_items}

        ORDER AMOUNT
        ------------------------------
        Subtotal: ₹{order.subtotal:.2f}
        Delivery Charge: ₹{order.delivery_charge:.2f}
        Total: ₹{order.total_amount:.2f}

        PAYMENT
        ------------------------------
        Method: {order.get_payment_method_display()}
        Status: {order.get_payment_status_display()}

        ORDER STATUS
        ------------------------------
        {order.get_status_display()}

        DELIVERY ADDRESS
        ------------------------------
        {order.full_name}
        {order.address_line1}
        {order.address_line2 or ""}
        {order.landmark or ""}
        {order.city}, {order.state} - {order.pincode}
        Phone: {order.phone_number}

        Please check the Django admin panel
        for complete order information.

        Rajanna Dairy Farm
        """

        admin_html = f"""
        <h2>New Order Received</h2>
        <p><strong>Order Number:</strong> {order.order_number}</p>

        <h3>Customer</h3>
        <p>Name: {order.user.full_name}<br>
        Email: {order.user.email}<br>
        Phone: {order.phone_number}</p>

        <h3>Order Items</h3>
        <p>{customer_items}</p>

        <h3>Order Amount</h3>
        <p>Subtotal: ₹{order.subtotal:.2f}<br>
        Delivery Charge: ₹{order.delivery_charge:.2f}<br>
        Total: ₹{order.total_amount:.2f}</p>

        <h3>Payment</h3>
        <p>Method: {order.get_payment_method_display()}<br>
        Status: {order.get_payment_status_display()}</p>

        <h3>Order Status</h3>
        <p>{order.get_status_display()}</p>

        <h3>Delivery Address</h3>
        <p>
        {order.full_name}<br>
        {order.address_line1}<br>
        {order.address_line2 or ""}<br>
        {order.landmark or ""}<br>
        {order.city}, {order.state} - {order.pincode}<br>
        Phone: {order.phone_number}
        </p>

        <p>Please check the Django admin panel for complete order information.</p>
        <p>Rajanna Dairy Farm</p>
        """

        resend.Emails.send({
            "from": "Rajanna Dairy Farm <onboarding@resend.dev>",
            "to": [settings.ADMIN_EMAIL],
            "subject": admin_subject,
            "text": admin_text,
            "html": admin_html,
        })


    except Exception:
        logger.exception(
            "Failed to send order emails for order_id=%s",
            order_id,
        )
        
        
        

import logging

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError, IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect

from .models import (
    Address,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Product,
)


logger = logging.getLogger(__name__)


@login_required
def place_order(request):

    if request.method != "POST":
        return redirect("checkout")

    selected_address_id = request.POST.get("selected_address")
    payment_method = request.POST.get("payment_method")
    checkout_token = request.POST.get("checkout_token")
    session_checkout_token = request.session.get(
    "checkout_token"
)


    if not checkout_token:
        messages.error(
            request,
            "Invalid checkout request. Please try again."
        )
        return redirect("checkout")

    if not session_checkout_token:
        messages.error(
            request,
            "This checkout session has expired. Please try again."
        )
        return redirect("checkout")

    if checkout_token != session_checkout_token:
        messages.error(
            request,
            "This checkout request has already been processed or has expired."
        )
        return redirect("checkout")
    # --------------------------------------------------
    # BASIC VALIDATION
    # --------------------------------------------------

    if not selected_address_id:
        messages.error(
            request,
            "Please select a delivery address."
        )
        return redirect("checkout")

    allowed_payment_methods = {
        choice[0]
        for choice in Order.PAYMENT_METHOD_CHOICES
    }

    if payment_method not in allowed_payment_methods:
        messages.error(
            request,
            "Invalid payment method."
        )
        return redirect("checkout")

    # --------------------------------------------------
    # ADDRESS VALIDATION
    # --------------------------------------------------

    address = (
        Address.objects
        .filter(
            id=selected_address_id,
            user=request.user
        )
        .first()
    )

    if not address:
        messages.error(
            request,
            "The selected address is invalid."
        )
        return redirect("checkout")

    try:

        # ==================================================
        # EVERYTHING BELOW IS ONE DATABASE TRANSACTION
        # ==================================================

        with transaction.atomic():

            # ----------------------------------------------
            # LOCK USER CART
            # ----------------------------------------------

            cart = (
                Cart.objects
                .select_for_update()
                .filter(user=request.user)
                .first()
            )

            if not cart:
                raise ValueError(
                    "Your cart is empty."
                )

            # ----------------------------------------------
            # GET CART ITEMS
            # ----------------------------------------------

            cart_items = list(
                CartItem.objects
                .filter(cart=cart)
                .select_related("product")
            )

            if not cart_items:
                raise ValueError(
                    "Your cart is empty."
                )

            # ----------------------------------------------
            # PRODUCT IDS
            # ----------------------------------------------

            product_ids = [
                item.product_id
                for item in cart_items
            ]

            # ----------------------------------------------
            # LOCK PRODUCTS
            # ----------------------------------------------

            locked_products = {
                product.id: product
                for product in (
                    Product.objects
                    .select_for_update()
                    .filter(id__in=product_ids)
                )
            }

            subtotal = Decimal("0.00")

            validated_items = []

            # ----------------------------------------------
            # VALIDATE PRODUCTS + STOCK + PRICE
            # ----------------------------------------------

            for cart_item in cart_items:

                product = locked_products.get(
                    cart_item.product_id
                )

                if not product:

                    raise ValueError(
                        "A product in your cart is no longer available."
                    )

                # ------------------------------------------
                # ACTIVE CHECK
                # ------------------------------------------

                if not product.is_active:

                    raise ValueError(
                        f"{product.name} is no longer available."
                    )

                # ------------------------------------------
                # STOCK CHECK
                # ------------------------------------------

                if (
                    not product.is_in_stock
                    or product.stock_quantity <= 0
                ):

                    raise ValueError(
                        f"{product.name} is currently out of stock."
                    )

                # ------------------------------------------
                # QUANTITY CHECK
                # ------------------------------------------

                if cart_item.quantity <= 0:

                    raise ValueError(
                        f"Invalid quantity for {product.name}."
                    )

                # ------------------------------------------
                # STOCK LIMIT
                # ------------------------------------------

                if (
                    cart_item.quantity
                    > product.stock_quantity
                ):

                    raise ValueError(
                        f"Only {product.stock_quantity} "
                        f"{product.unit} of {product.name} "
                        f"is available."
                    )

                # ------------------------------------------
                # FRESH PRICE FROM DATABASE
                # ------------------------------------------

                unit_price = (
                    product.selling_price
                ).quantize(
                    Decimal("0.01")
                )

                item_total = (
                    unit_price * cart_item.quantity
                ).quantize(
                    Decimal("0.01")
                )

                subtotal += item_total

                validated_items.append({
                    "product": product,
                    "quantity": cart_item.quantity,
                    "unit_price": unit_price,
                    "discount_percentage": (
                        product.discount_percentage
                    ),
                    "total_price": item_total,
                })

            # ----------------------------------------------
            # DELIVERY CHARGE
            # ----------------------------------------------

            delivery_charge = Decimal("0.00")

            # ----------------------------------------------
            # FINAL TOTAL
            # ----------------------------------------------

            total_amount = (
                subtotal + delivery_charge
            ).quantize(
                Decimal("0.01")
            )

            # ----------------------------------------------
            # COD PAYMENT
            # ----------------------------------------------

            if payment_method == "cod":

                payment_status = "pending"

            else:

                raise ValueError(
                    "This payment method is currently unavailable."
                )

            # ----------------------------------------------
            # CREATE ORDER
            # ----------------------------------------------

            order = Order.objects.create(

                user=request.user,

                # Address snapshot
                full_name=address.full_name,
                phone_number=address.phone_number,
                address_line1=address.address_line1,
                address_line2=address.address_line2,
                landmark=address.landmark,
                city=address.city,
                state=address.state,
                pincode=address.pincode,

                # Amounts
                subtotal=subtotal,
                delivery_charge=delivery_charge,
                total_amount=total_amount,

                # Payment
                payment_method=payment_method,
                payment_status=payment_status,

                # Status
                status="pending",
            )

            # ----------------------------------------------
            # CREATE ORDER ITEMS
            # ----------------------------------------------

            for item in validated_items:

                product = item["product"]

                OrderItem.objects.create(

                    order=order,

                    product=product,

                    # Product snapshot
                    product_name=product.name,
                    sku=product.sku,
                    unit=product.unit,

                    quantity=item["quantity"],

                    unit_price=item["unit_price"],

                    discount_percentage=(
                        item["discount_percentage"]
                    ),

                    total_price=item["total_price"],
                )

                # ------------------------------------------
                # REDUCE STOCK
                # ------------------------------------------

                product.stock_quantity -= (
                    item["quantity"]
                )

                product.is_in_stock = (
                    product.stock_quantity > 0
                )

                product.save(
                    update_fields=[
                        "stock_quantity",
                        "is_in_stock",
                        "updated_at",
                    ]
                )

            # ----------------------------------------------
            # CLEAR CART
            # ----------------------------------------------

            CartItem.objects.filter(
                cart=cart
            ).delete()
            
            transaction.on_commit(
                lambda order_id=order.pk:
                    send_order_confirmation_emails(order_id)
            )
            
            
            
        

        # ==================================================
        # TRANSACTION SUCCESSFULLY COMMITTED
        # ==================================================

        # messages.success(
        #     request,
        #     f"Order {order.order_number} placed successfully."
        # )

        # return redirect(
        #     "order-success",
        #     order_number=order.order_number
        # )
        
                # ==================================================
        # TRANSACTION SUCCESSFULLY COMMITTED
        # ==================================================

        request.session.pop("checkout_token", None)
        request.session.modified = True
        print("orrerid==",order.pk)
        
        print("1123")
        messages.success(
            request,
            f"Order {order.order_number} placed successfully."
        )

        return redirect(
            "order-success",
            order_number=order.order_number
        )

    # ======================================================
    # BUSINESS / VALIDATION ERROR
    # ======================================================

    except ValueError as e:

        messages.error(
            request,
            str(e)
        )

        return redirect("checkout")

    # ======================================================
    # DATABASE INTEGRITY ERROR
    # ======================================================

    except IntegrityError:

        logger.exception(
            "Integrity error while placing order "
            "for user_id=%s",
            request.user.id
        )

        messages.error(
            request,
            "We couldn't place your order right now. "
            "Please try again."
        )

        return redirect("checkout")

    # ======================================================
    # OTHER DATABASE ERROR
    # ======================================================

    except DatabaseError:

        logger.exception(
            "Database error while placing order "
            "for user_id=%s",
            request.user.id
        )

        messages.error(
            request,
            "We couldn't process your order right now. "
            "Please try again."
        )

        return redirect("checkout")

    # ======================================================
    # UNEXPECTED ERROR
    # ======================================================

    except Exception:

        logger.exception(
            "Unexpected error while placing order "
            "for user_id=%s",
            request.user.id
        )

        messages.error(
            request,
            "Something went wrong while placing your order. "
            "Please try again."
        )

        return redirect("checkout")




@login_required
def order_success(request, order_number):

    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user
    )

    return render(
        request,
        "order_success.html",
        {
            "order": order,
        }
    )
    
    
    



@login_required
def my_orders(request):

    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items")
        .order_by("-created_at")
    )

    return render(
        request,
        "my_orders.html",
        {
            "orders": orders,
        }
    )
    



@login_required
def order_detail(request, order_number):

    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        order_number=order_number,
        user=request.user
    )

    return render(
        request,
        "order_detail.html",
        {
            "order": order,
        }
    )
    
    



@login_required
def order_tracking(request, order_number):

    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        order_number=order_number,
        user=request.user
    )

    status_flow = [
        {
            "key": "pending",
            "label": "Order Placed",
            "description": "Your order has been received."
        },
        {
            "key": "confirmed",
            "label": "Confirmed",
            "description": "Your order has been confirmed."
        },
        {
            "key": "processing",
            "label": "Processing",
            "description": "Your order is being prepared."
        },
        {
            "key": "shipped",
            "label": "Shipped",
            "description": "Your order has been shipped."
        },
        {
            "key": "out_for_delivery",
            "label": "Out for Delivery",
            "description": "Your order is on the way."
        },
        {
            "key": "delivered",
            "label": "Delivered",
            "description": "Your order has been delivered."
        },
    ]

    status_keys = [
        item["key"]
        for item in status_flow
    ]

    if order.status in status_keys:
        current_index = status_keys.index(
            order.status
        )
    else:
        current_index = 0

    for index, item in enumerate(status_flow):

        if index < current_index:
            item["state"] = "completed"

        elif index == current_index:
            item["state"] = "current"

        else:
            item["state"] = "pending"

    return render(
        request,
        "order_tracking.html",
        {
            "order": order,
            "status_flow": status_flow,
        }
    )










from django.contrib.auth import logout
from django.shortcuts import redirect


def user_logout(request):
    """
    Securely log out the current user and clear session data.
    """

    # Django logout clears the authenticated user's session.
    logout(request)

    # Explicitly clear any remaining session data.
    request.session.flush()

    # Redirect to home page.
    response = redirect("/shop")

    # Expire Django session cookie immediately.
    response.delete_cookie(
        "sessionid",
        path="/",
        samesite="Lax",
    )

    return response





from django.utils.http import url_has_allowed_host_and_scheme

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from .models import Subscriber


@require_http_methods(["GET", "POST"])
def subscribe(request):
    
    # ---------------------------------------------
        # GET request
        # ---------------------------------------------
    
    if request.method == "GET":
        return render(
                request,
                "subscribe.html"
            )
    """
    Subscribe an email address to the newsletter.

    The user is redirected back to the page where
    the subscription form was submitted.
    """

    email = request.POST.get("email", "").strip().lower()
    next_url = request.POST.get("next", "").strip()
    
    # print(next_url)

    # -------------------------------------------------
    # VALIDATE REDIRECT URL
    # -------------------------------------------------

    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = ""

    # -------------------------------------------------
    # VALIDATE EMAIL
    # -------------------------------------------------

    if not email:
        messages.error(
            request,
            "Please enter your email address."
        )

        if next_url:
            return redirect(next_url)

        return redirect("subscribe")

    try:
        validate_email(email)
    except ValidationError:
        messages.error(
            request,
            "Please enter a valid email address."
        )

        if next_url:
            return redirect(next_url)

        return redirect("subscribe")

    # -------------------------------------------------
    # SAVE SUBSCRIBER
    # -------------------------------------------------

    try:
        subscriber, created = Subscriber.objects.get_or_create(
            email=email
        )

        if created:
            messages.success(
                request,
                "You have successfully subscribed!"
            )
        else:
            messages.info(
                request,
                "This email is already subscribed."
            )

    except IntegrityError:
        messages.info(
            request,
            "This email is already subscribed."
        )

    # -------------------------------------------------
    # RETURN TO SAME PAGE
    # -------------------------------------------------

    if next_url:
        return redirect(next_url)

    return redirect("subscribe")
















from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import (
    MilkSubscription,
    MilkDelivery,
    MilkBill,
)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone


# @login_required
# def my_milk_subscription(request):
#     user = request.user

#     subscription = (
#         MilkSubscription.objects
#         .filter(
#             user=user,
#             status__in=["active", "paused"],
#         )
#         .select_related("address")
#         .prefetch_related(
#             "items__product",
#         )
#         .first()
#     )

#     if not subscription:
#         return render(
#             request,
#             "my_milk_subscription.html",
#             {
#                 "subscription": None,
#                 "today_delivery": None,
#                 "recent_deliveries": [],
#                 "current_bill": None,
#             },
#         )

#     today = timezone.localdate()

#     today_delivery = (
#         MilkDelivery.objects
#         .filter(
#             subscription=subscription,
#             delivery_date=today,
#         )
#         .select_related(
#             "subscription_item",
#             "subscription_item__product",
#         )
#         .first()
#     )

#     recent_deliveries = (
#         MilkDelivery.objects
#         .filter(
#             subscription=subscription,
#         )
#         .select_related(
#             "subscription_item",
#             "subscription_item__product",
#         )
#         .order_by(
#             "-delivery_date",
#             "-created_at",
#         )[:15]
#     )

#     current_bill = (
#         MilkBill.objects
#         .filter(
#             subscription=subscription,
#             billing_month=today.month,
#             billing_year=today.year,
#         )
#         .first()
#     )

#     context = {
#         "subscription": subscription,
#         "today_delivery": today_delivery,
#         "recent_deliveries": recent_deliveries,
#         "current_bill": current_bill,
#     }

#     return render(
#         request,
#         "my_milk_subscription.html",
#         context,
#     )
    
    
    
    

# @login_required
# def my_milk_subscription(request):

#     user = request.user

#     subscription = (
#         MilkSubscription.objects
#         .filter(
#             user=user,
#             status__in=["pending", "active", "paused"],
#         )
#         .select_related("address")
#         .prefetch_related("items__product")
#         .first()
#     )

#     if not subscription:
#         return render(
#             request,
#             "my_milk_subscription.html",
#             {
#                 "subscription": None,
#                 "today_delivery": None,
#                 "recent_deliveries": [],
#                 "current_bill": None,
#             },
#         )

#     today = timezone.localdate()

#     today_delivery = None
#     recent_deliveries = []
#     current_bill = None

#     # Delivery/billing information only makes sense
#     # once the subscription is active.
#     if subscription.status == "active":

#         today_delivery = (
#             MilkDelivery.objects
#             .filter(
#                 subscription=subscription,
#                 delivery_date=today,
#             )
#             .select_related(
#                 "subscription_item",
#                 "subscription_item__product",
#             )
#             .first()
#         )

#         recent_deliveries = (
#             MilkDelivery.objects
#             .filter(subscription=subscription)
#             .select_related(
#                 "subscription_item",
#                 "subscription_item__product",
#             )
#             .order_by(
#                 "-delivery_date",
#                 "-created_at",
#             )[:15]
#         )

#         current_bill = (
#             MilkBill.objects
#             .filter(
#                 subscription=subscription,
#                 billing_month=today.month,
#                 billing_year=today.year,
#             )
#             .first()
#         )

#     return render(
#         request,
#         "my_milk_subscription.html",
#         {
#             "subscription": subscription,
#             "today_delivery": today_delivery,
#             "recent_deliveries": recent_deliveries,
#             "current_bill": current_bill,
#         },
#     )



@login_required
def my_milk_subscription(request):

    user = request.user

    subscription = (
        MilkSubscription.objects
        .filter(
            user=user,
            status__in=[
                "pending",
                "active",
                "paused",
            ],
        )
        .select_related("address")
        .prefetch_related(
            "items__product",
        )
        .first()
    )

    if not subscription:
        return render(
            request,
            "my_milk_subscription.html",
            {
                "subscription": None,
                "today_delivery": None,
                "recent_deliveries": [],
                "current_bill": None,
                "bill_history": [],
            },
        )

    today = timezone.localdate()

    today_delivery = None
    recent_deliveries = []
    current_bill = None
    bill_history = []

    # --------------------------------------------------
    # ACTIVE SUBSCRIPTION DATA
    # --------------------------------------------------

    if subscription.status == "active":

        # Today's delivery
        today_delivery = (
            MilkDelivery.objects
            .filter(
                subscription=subscription,
                delivery_date=today,
            )
            .select_related(
                "subscription_item",
                "subscription_item__product",
            )
            .first()
        )

        # Recent deliveries
        recent_deliveries = (
            MilkDelivery.objects
            .filter(
                subscription=subscription,
            )
            .select_related(
                "subscription_item",
                "subscription_item__product",
            )
            .order_by(
                "-delivery_date",
                "-created_at",
            )[:15]
        )

        # Current month bill
        current_bill = (
            MilkBill.objects
            .filter(
                subscription=subscription,
                billing_month=today.month,
                billing_year=today.year,
            )
            .first()
        )

        # Billing history
        bill_history = (
            MilkBill.objects
            .filter(
                subscription=subscription,
            )
            .order_by(
                "-billing_year",
                "-billing_month",
            )[:12]
        )

    return render(
        request,
        "my_milk_subscription.html",
        {
            "subscription": subscription,
            "today_delivery": today_delivery,
            "recent_deliveries": recent_deliveries,
            "current_bill": current_bill,
            "bill_history": bill_history,
        },
    )





from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import (
    Address,
    MilkSubscription,
    MilkSubscriptionItem,
    MilkDelivery,
    MilkBill,
    Product,
)



@login_required
def create_milk_subscription(request):

    user = request.user

    addresses = (
        Address.objects
        .filter(user=user)
        .order_by("-is_default", "-created_at")
    )

    products = (
        Product.objects
        .filter(
            is_active=True,
            is_in_stock=True,
            stock_quantity__gt=0,
        )
        .select_related("category")
        .order_by("name")
    )

    if request.method == "POST":

        product_id = request.POST.get("product_id", "").strip()
        address_id = request.POST.get("address_id", "").strip()
        quantity_value = request.POST.get("quantity", "").strip()
        start_date_value = request.POST.get("start_date", "").strip()

        # -------------------------
        # Basic validation
        # -------------------------

        if not product_id:
            messages.error(request, "Please select a milk product.")
            return render(
                request,
                "create_milk_subscription.html",
                {
                    "addresses": addresses,
                    "products": products,
                },
            )

        if not address_id:
            messages.error(request, "Please select a delivery address.")
            return render(
                request,
                "create_milk_subscription.html",
                {
                    "addresses": addresses,
                    "products": products,
                },
            )

        if not quantity_value:
            messages.error(request, "Please enter the quantity.")
            return render(
                request,
                "create_milk_subscription.html",
                {
                    "addresses": addresses,
                    "products": products,
                },
            )

        if not start_date_value:
            messages.error(request, "Please select a start date.")
            return render(
                request,
                "create_milk_subscription.html",
                {
                    "addresses": addresses,
                    "products": products,
                },
            )

        # -------------------------
        # Product validation
        # -------------------------

        product = get_object_or_404(
            Product.objects.filter(
                id=product_id,
                is_active=True,
                is_in_stock=True,
                stock_quantity__gt=0,
            ),
            id=product_id,
        )

        # -------------------------
        # Address validation
        # -------------------------

        address = get_object_or_404(
            Address,
            id=address_id,
            user=user,
        )

        # -------------------------
        # Quantity validation
        # -------------------------

        try:
            quantity = int(quantity_value)
        except (TypeError, ValueError):
            messages.error(request, "Please enter a valid quantity.")
            return render(
                request,
                "create_milk_subscription.html",
                {
                    "addresses": addresses,
                    "products": products,
                },
            )

        if quantity < 1:
            messages.error(request, "Quantity must be at least 1.")
            return render(
                request,
                "create_milk_subscription.html",
                {
                    "addresses": addresses,
                    "products": products,
                },
            )

        if Decimal(quantity) > product.stock_quantity:
            messages.error(
                request,
                f"Only {product.stock_quantity} units are currently available."
            )
            return render(
                request,
                "create_milk_subscription.html",
                {
                    "addresses": addresses,
                    "products": products,
                },
            )

        # -------------------------
        # Start date validation
        # -------------------------

        try:
            start_date = timezone.datetime.strptime(
                start_date_value,
                "%Y-%m-%d",
            ).date()
        except (TypeError, ValueError):
            messages.error(request, "Please select a valid start date.")
            return render(
                request,
                "create_milk_subscription.html",
                {
                    "addresses": addresses,
                    "products": products,
                },
            )

        today = timezone.localdate()

        if start_date < today:
            messages.error(
                request,
                "Subscription start date cannot be in the past."
            )
            return render(
                request,
                "create_milk_subscription.html",
                {
                    "addresses": addresses,
                    "products": products,
                },
            )

        # -------------------------
        # Prevent duplicate request
        # -------------------------

        existing_subscription = (
            MilkSubscription.objects
            .filter(
                user=user,
                status__in=["pending", "active"],
            )
            .first()
        )

        if existing_subscription:
            messages.info(
                request,
                "You already have an active subscription or a pending subscription request."
            )
            return redirect("my-milk-subscription")

        # -------------------------
        # Create subscription
        # -------------------------

        with transaction.atomic():

            subscription = MilkSubscription.objects.create(
                user=user,
                address=address,
                start_date=start_date,
                billing_cycle="monthly",
                status="pending",
            )

            MilkSubscriptionItem.objects.create(
                subscription=subscription,
                product=product,
                quantity=quantity,
                price_per_unit=product.selling_price,
                frequency="daily",
                start_date=start_date,
            )

        messages.success(
            request,
            "Your milk subscription request has been submitted successfully. "
            "Our team will review and activate it."
        )

        return redirect("my-milk-subscription")

    return render(
        request,
        "create_milk_subscription.html",
        {
            "addresses": addresses,
            "products": products,
        },
    )


