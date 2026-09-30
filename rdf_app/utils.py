# from django.core.mail import EmailMultiAlternatives
# from django.utils.html import strip_tags


# def send_milk_bill_email(bill):

#     subscription = (
#         bill.subscription
#     )

#     user = subscription.user

#     customer_name = (
#         user.get_full_name()
#         if hasattr(user, "get_full_name")
#         else ""
#     )

#     if not customer_name:
#         customer_name = user.email

#     billing_period = (
#         f"{bill.billing_month:02d}/{bill.billing_year}"
#     )

#     subject = (
#         f"Rajanna Dairy Farm - "
#         f"Milk Bill for {billing_period}"
#     )

#     html_message = f"""
#     <html>
#         <body>

#             <h2>Rajanna Dairy Farm</h2>

#             <p>Dear {customer_name},</p>

#             <p>
#                 Your monthly milk bill has been generated.
#             </p>

#             <h3>Bill Details</h3>

#             <table cellpadding="8" cellspacing="0" border="1">

#                 <tr>
#                     <td><strong>Subscription</strong></td>
#                     <td>{subscription.subscription_number}</td>
#                 </tr>

#                 <tr>
#                     <td><strong>Billing Period</strong></td>
#                     <td>{billing_period}</td>
#                 </tr>

#                 <tr>
#                     <td><strong>Total Amount</strong></td>
#                     <td>₹{bill.total_amount}</td>
#                 </tr>

#                 <tr>
#                     <td><strong>Paid Amount</strong></td>
#                     <td>₹{bill.paid_amount}</td>
#                 </tr>

#                 <tr>
#                     <td><strong>Pending Amount</strong></td>
#                     <td>₹{bill.pending_amount}</td>
#                 </tr>

#                 <tr>
#                     <td><strong>Status</strong></td>
#                     <td>{bill.get_status_display()}</td>
#                 </tr>

#             </table>

#             <h3>Payment Method</h3>

#             <p>
#                 Cash payment
#             </p>

#             <p>
#                 Please pay the pending amount to
#                 Rajanna Dairy Farm.
#             </p>

#             <p>
#                 Thank you for choosing Rajanna Dairy Farm.
#             </p>

#             <br>

#             <p>
#                 Regards,<br>
#                 <strong>Rajanna Dairy Farm</strong>
#             </p>

#         </body>
#     </html>
#     """

#     plain_message = strip_tags(html_message)

#     email = EmailMultiAlternatives(
#         subject=subject,
#         body=plain_message,
#         from_email=None,
#         to=[user.email],
#     )

#     email.attach_alternative(
#         html_message,
#         "text/html",
#     )

#     email.send(
#         fail_silently=False,
#     )
    
    
    
    


# from django.conf import settings
# from django.contrib.auth import get_user_model
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags

# def send_new_product_announcement(product, product_url):
#     """
#     Send a new-product announcement to:

#     1. All registered users
#     2. All subscribers

#     Includes inactive users.
#     Duplicate email addresses are removed.
#     """

#     from .models import Subscriber

#     User = get_user_model()

#     # ---------------------------------------------------------
#     # 1. Get all registered users
#     # ---------------------------------------------------------
#     user_emails = User.objects.values_list(
#         "email",
#         flat=True
#     )

#     # ---------------------------------------------------------
#     # 2. Get all subscribers
#     # ---------------------------------------------------------
#     subscriber_emails = Subscriber.objects.values_list(
#         "email",
#         flat=True
#     )

#     # ---------------------------------------------------------
#     # 3. Combine and remove duplicates
#     # ---------------------------------------------------------
#     recipient_emails = {
#         email.strip().lower()
#         for email in list(user_emails) + list(subscriber_emails)
#         if email and email.strip()
#     }

#     if not recipient_emails:
#         return {
#             "total": 0,
#             "sent": 0,
#             "failed": 0,
#             "failed_emails": [],
#         }

#     # ---------------------------------------------------------
#     # 4. Product information
#     # ---------------------------------------------------------
#     product_name = product.name
#     selling_price = product.selling_price
#     original_price = product.price
#     discount_percentage = product.discount_percentage

#     # ---------------------------------------------------------
#     # 5. Product image
#     # ---------------------------------------------------------
#     image_url = ""

#     try:
#         if product.main_image:
#             image_url = product.get_image_url(
#                 width=800,
#                 height=800
#             )
#     except Exception:
#         image_url = ""

#     # ---------------------------------------------------------
#     # 6. Email subject
#     # ---------------------------------------------------------
#     subject = f"New Product at Rajanna Dairy Farm - {product_name}"

#     sent = 0
#     failed = 0
#     failed_emails = []

#     # ---------------------------------------------------------
#     # 7. Send individually
#     # ---------------------------------------------------------
#     for email in recipient_emails:

#         try:
#             html_content = render_to_string(
#                 "emails/new_product.html",
#                 {
#                     "product": product,
#                     "product_name": product_name,
#                     "selling_price": selling_price,
#                     "original_price": original_price,
#                     "discount_percentage": discount_percentage,
#                     "image_url": image_url,
#                     "product_url": product_url,
#                 }
#             )

#             text_content = strip_tags(html_content)

#             email_message = EmailMultiAlternatives(
#                 subject=subject,
#                 body=text_content,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 to=[email],
#             )

#             email_message.attach_alternative(
#                 html_content,
#                 "text/html"
#             )

#             email_message.send(
#                 fail_silently=False
#             )

#             sent += 1

#         except Exception as exc:
#             failed += 1
#             failed_emails.append(
#                 {
#                     "email": email,
#                     "error": str(exc),
#                 }
#             )

#     return {
#         "total": len(recipient_emails),
#         "sent": sent,
#         "failed": failed,
#         "failed_emails": failed_emails,
#     }
    
    
    


import resend

from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# ============================================================
# RESEND CONFIGURATION
# ============================================================

def _configure_resend():
    """
    Configure Resend using the API key from Django settings.
    """

    api_key = getattr(
        settings,
        "RESEND_API_KEY",
        None
    )

    if not api_key:
        raise RuntimeError(
            "RESEND_API_KEY is not configured."
        )

    resend.api_key = api_key


def _get_from_email():
    """
    Return the configured Resend sender.
    """

    return getattr(
        settings,
        "RESEND_FROM_EMAIL",
        "Rajanna Dairy Farm <onboarding@resend.dev>"
    )


# ============================================================
# MILK BILL EMAIL
# ============================================================

def send_milk_bill_email(bill):

    _configure_resend()

    subscription = bill.subscription
    user = subscription.user

    if not user.email:
        return {
            "success": False,
            "error": "Customer does not have an email address."
        }

    customer_name = ""

    if hasattr(user, "get_full_name"):
        customer_name = user.get_full_name()

    if not customer_name:
        customer_name = user.email

    billing_period = (
        f"{bill.billing_month:02d}/"
        f"{bill.billing_year}"
    )

    subject = (
        "Rajanna Dairy Farm - "
        f"Milk Bill for {billing_period}"
    )

    html_message = f"""
    <html>
        <body
            style="
                font-family: Arial, sans-serif;
                color: #333333;
                line-height: 1.6;
            "
        >

            <div
                style="
                    max-width: 650px;
                    margin: auto;
                    padding: 20px;
                "
            >

                <h2
                    style="
                        color: #176b45;
                    "
                >
                    Rajanna Dairy Farm
                </h2>

                <p>
                    Dear {customer_name},
                </p>

                <p>
                    Your monthly milk bill has been generated.
                </p>

                <h3>
                    Bill Details
                </h3>

                <table
                    cellpadding="10"
                    cellspacing="0"
                    style="
                        width: 100%;
                        border-collapse: collapse;
                    "
                >

                    <tr>
                        <td
                            style="
                                border: 1px solid #dddddd;
                            "
                        >
                            <strong>
                                Subscription
                            </strong>
                        </td>

                        <td
                            style="
                                border: 1px solid #dddddd;
                            "
                        >
                            {subscription.subscription_number}
                        </td>
                    </tr>

                    <tr>
                        <td
                            style="
                                border: 1px solid #dddddd;
                            "
                        >
                            <strong>
                                Billing Period
                            </strong>
                        </td>

                        <td
                            style="
                                border: 1px solid #dddddd;
                            "
                        >
                            {billing_period}
                        </td>
                    </tr>

                    <tr>
                        <td
                            style="
                                border: 1px solid #dddddd;
                            "
                        >
                            <strong>
                                Total Amount
                            </strong>
                        </td>

                        <td
                            style="
                                border: 1px solid #dddddd;
                            "
                        >
                            ₹{bill.total_amount}
                        </td>
                    </tr>

                    <tr>
                        <td
                            style="
                                border: 1px solid #dddddd;
                            "
                        >
                            <strong>
                                Paid Amount
                            </strong>
                        </td>

                        <td
                            style="
                                border: 1px solid #dddddd;
                            "
                        >
                            ₹{bill.paid_amount}
                        </td>
                    </tr>

                    <tr>
                        <td
                            style="
                                border: 1px solid #dddddd;
                            "
                        >
                            <strong>
                                Pending Amount
                            </strong>
                        </td>

                        <td
                            style="
                                border: 1px solid #dddddd;
                            "
                        >
                            ₹{bill.pending_amount}
                        </td>
                    </tr>

                    <tr>
                        <td
                            style="
                                border: 1px solid #dddddd;
                            "
                        >
                            <strong>
                                Status
                            </strong>
                        </td>

                        <td
                            style="
                                border: 1px solid #dddddd;
                            "
                        >
                            {bill.get_status_display()}
                        </td>
                    </tr>

                </table>

                <h3>
                    Payment Method
                </h3>

                <p>
                    Cash payment
                </p>

                <p>
                    Please pay the pending amount to
                    Rajanna Dairy Farm.
                </p>

                <p>
                    Thank you for choosing
                    Rajanna Dairy Farm.
                </p>

                <br>

                <p>
                    Regards,
                    <br>

                    <strong>
                        Rajanna Dairy Farm
                    </strong>
                </p>

            </div>

        </body>
    </html>
    """

    try:

        response = resend.Emails.send({
            "from": _get_from_email(),

            "to": [
                user.email
            ],

            "subject": subject,

            "html": html_message,
        })

        print(
            "MILK BILL EMAIL RESULT ==",
            response
        )

        return {
            "success": True,
            "result": response
        }

    except Exception as exc:

        print(
            "MILK BILL EMAIL ERROR ==",
            repr(exc)
        )

        return {
            "success": False,
            "error": str(exc)
        }


# ============================================================
# NEW PRODUCT ANNOUNCEMENT
# ============================================================

def send_new_product_announcement(
    product,
    product_url
):
    """
    Send new-product announcement emails.

    Recipients:
    1. Registered users
    2. Subscribers

    Duplicate emails are removed.

    IMPORTANT:
    While using Resend's onboarding@resend.dev testing
    sender, Resend normally allows sending only to the
    verified/account email.

    Once your own domain is verified, set
    RESEND_FROM_EMAIL to your domain email and enable
    sending to all customers.
    """

    _configure_resend()

    from .models import Subscriber

    User = get_user_model()

    # --------------------------------------------------------
    # REGISTERED USERS
    # --------------------------------------------------------

    user_emails = User.objects.values_list(
        "email",
        flat=True
    )


    # --------------------------------------------------------
    # SUBSCRIBERS
    # --------------------------------------------------------

    subscriber_emails = (
        Subscriber.objects.values_list(
            "email",
            flat=True
        )
    )


    # --------------------------------------------------------
    # COMBINE + REMOVE DUPLICATES
    # --------------------------------------------------------

    recipient_emails = {
        email.strip().lower()
        for email in (
            list(user_emails)
            +
            list(subscriber_emails)
        )
        if email and email.strip()
    }


    # --------------------------------------------------------
    # RESEND TEST MODE
    # --------------------------------------------------------

    resend_test_mode = getattr(
        settings,
        "RESEND_TEST_MODE",
        True
    )

    if resend_test_mode:

        admin_email = getattr(
            settings,
            "ADMIN_EMAIL",
            None
        )

        if not admin_email:
            raise RuntimeError(
                "ADMIN_EMAIL is required "
                "when RESEND_TEST_MODE=True."
            )

        recipient_emails = {
            admin_email.strip().lower()
        }


    # --------------------------------------------------------
    # NO RECIPIENTS
    # --------------------------------------------------------

    if not recipient_emails:

        return {
            "total": 0,
            "sent": 0,
            "failed": 0,
            "failed_emails": [],
        }


    # --------------------------------------------------------
    # PRODUCT INFORMATION
    # --------------------------------------------------------

    product_name = product.name
    selling_price = product.selling_price
    original_price = product.price
    discount_percentage = (
        product.discount_percentage
    )


    # --------------------------------------------------------
    # PRODUCT IMAGE
    # --------------------------------------------------------

    image_url = ""

    try:

        if product.main_image:

            image_url = product.get_image_url(
                width=800,
                height=800
            )

    except Exception as exc:

        print(
            "PRODUCT IMAGE URL ERROR ==",
            repr(exc)
        )

        image_url = ""


    # --------------------------------------------------------
    # EMAIL SUBJECT
    # --------------------------------------------------------

    subject = (
        "New Product at Rajanna Dairy Farm - "
        f"{product_name}"
    )


    # --------------------------------------------------------
    # RENDER EMAIL TEMPLATE ONCE
    # --------------------------------------------------------

    html_content = render_to_string(
        "emails/new_product.html",
        {
            "product": product,
            "product_name": product_name,
            "selling_price": selling_price,
            "original_price": original_price,
            "discount_percentage":
                discount_percentage,
            "image_url": image_url,
            "product_url": product_url,
        }
    )


    sent = 0
    failed = 0
    failed_emails = []


    # --------------------------------------------------------
    # SEND INDIVIDUALLY
    # --------------------------------------------------------

    for email in recipient_emails:

        try:

            response = resend.Emails.send({
                "from": _get_from_email(),

                "to": [
                    email
                ],

                "subject": subject,

                "html": html_content,
            })

            sent += 1

            print(
                "PRODUCT EMAIL SENT ==",
                email,
                response
            )

        except Exception as exc:

            failed += 1

            failed_emails.append({
                "email": email,
                "error": str(exc),
            })

            print(
                "PRODUCT EMAIL FAILED ==",
                email,
                repr(exc)
            )


    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    return {
        "total": len(recipient_emails),
        "sent": sent,
        "failed": failed,
        "failed_emails": failed_emails,
    }