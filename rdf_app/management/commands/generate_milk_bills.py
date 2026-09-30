# from calendar import monthrange
# from datetime import date, timedelta
# from decimal import Decimal

# from django.core.management.base import BaseCommand
# from django.db import transaction
# from django.utils import timezone

# from rdf_app.models import (
#     MilkSubscription,
#     MilkSubscriptionItem,
#     MilkDelivery,
#     MilkBill,
# )

# from rdf_app.utils import send_milk_bill_email
# # from rdf_app.utils import send_milk_bill_email

# class Command(BaseCommand):
#     help = "Generate monthly milk bills from delivered milk records."

#     def add_arguments(self, parser):
#         parser.add_argument(
#             "--month",
#             type=int,
#             help="Billing month (1-12). Defaults to previous month.",
#         )

#         parser.add_argument(
#             "--year",
#             type=int,
#             help="Billing year. Defaults to previous month year.",
#         )

#     def handle(self, *args, **options):

#         today = timezone.localdate()

#         # --------------------------------------------------
#         # Determine billing period
#         # --------------------------------------------------

#         if options.get("month") and options.get("year"):

#             billing_month = options["month"]
#             billing_year = options["year"]

#             if billing_month < 1 or billing_month > 12:
#                 self.stdout.write(
#                     self.style.ERROR(
#                         "Month must be between 1 and 12."
#                     )
#                 )
#                 return

#         else:

#             first_day_current_month = today.replace(day=1)

#             previous_month_last_day = (
#                 first_day_current_month - timedelta(days=1)
#             )

#             billing_month = previous_month_last_day.month
#             billing_year = previous_month_last_day.year

#         # --------------------------------------------------
#         # Billing period dates
#         # --------------------------------------------------

#         first_day = date(
#             billing_year,
#             billing_month,
#             1,
#         )

#         last_day = date(
#             billing_year,
#             billing_month,
#             monthrange(
#                 billing_year,
#                 billing_month,
#             )[1],
#         )

#         self.stdout.write(
#             f"Generating milk bills for "
#             f"{billing_month:02d}/{billing_year}"
#         )

#         self.stdout.write(
#             f"Period: {first_day} to {last_day}"
#         )

#         # --------------------------------------------------
#         # Active subscriptions
#         # --------------------------------------------------

#         subscriptions = (
#             MilkSubscription.objects
#             .filter(
#                 status="active",
#                 start_date__lte=last_day,
#             )
#             .select_related(
#                 "user",
#                 "address",
#             )
#             .prefetch_related(
#                 "items",
#             )
#         )

#         generated_count = 0
#         skipped_count = 0
#         zero_bill_count = 0

#         # --------------------------------------------------
#         # Process subscriptions
#         # --------------------------------------------------

#         for subscription in subscriptions:

#             # ----------------------------------------------
#             # Don't generate duplicate bills
#             # ----------------------------------------------
            
#             existing_bill = (
#                 MilkBill.objects
#                 .filter(
#                     subscription=subscription,
#                     billing_month=billing_month,
#                     billing_year=billing_year,
#                 )
#                 .first()
#             )

           
            
#             if existing_bill:

#                 if not existing_bill.email_sent:

#                     result = send_milk_bill_email(
#                         existing_bill
#                     )

#                     if result.get("success"):

#                         existing_bill.email_sent = True
#                         existing_bill.email_sent_at = timezone.now()

#                         existing_bill.save(
#                             update_fields=[
#                                 "email_sent",
#                                 "email_sent_at",
#                                 "updated_at",
#                             ]
#                         )

#                         self.stdout.write(
#                             self.style.SUCCESS(
#                                 f"Email retry successful: "
#                                 f"{subscription.user.email}"
#                             )
#                         )

#                     else:

#                         self.stdout.write(
#                             self.style.ERROR(
#                                 f"Email retry failed for "
#                                 f"{subscription.subscription_number}: "
#                                 f"{result.get('error', 'Unknown error')}"
#                             )
#                         )

#                 else:

#                     self.stdout.write(
#                         self.style.WARNING(
#                             f"Bill already exists and email already sent: "
#                             f"{subscription.subscription_number}"
#                         )
#                     )

#                 skipped_count += 1
#                 continue

         

#             # ----------------------------------------------
#             # Get delivered milk records
#             # ----------------------------------------------

#             deliveries = (
#                 MilkDelivery.objects
#                 .filter(
#                     subscription=subscription,
#                     delivery_date__range=(
#                         first_day,
#                         last_day,
#                     ),
#                     status="delivered",
#                 )
#                 .select_related(
#                     "subscription_item",
#                     "subscription_item__product",
#                 )
#                 .order_by("delivery_date")
#             )

#             total_amount = Decimal("0.00")

#             delivered_days = 0

#             for delivery in deliveries:

#                 total_amount += (
#                     delivery.total_amount
#                 )

#                 delivered_days += 1

#             total_amount = total_amount.quantize(
#                 Decimal("0.01")
#             )

#             # ----------------------------------------------
#             # No delivered milk
#             # ----------------------------------------------

#             if total_amount <= Decimal("0.00"):

#                 self.stdout.write(
#                     self.style.WARNING(
#                         f"No delivered milk: "
#                         f"{subscription.subscription_number}"
#                     )
#                 )

#                 zero_bill_count += 1
#                 continue

#             # ----------------------------------------------
#             # Create bill
#             # ----------------------------------------------

#             with transaction.atomic():

#                 bill = MilkBill.objects.create(
#                     subscription=subscription,
#                     billing_month=billing_month,
#                     billing_year=billing_year,
#                     total_amount=total_amount,
#                     paid_amount=Decimal("0.00"),
#                     notes=(
#                         f"Generated automatically. "
#                         f"Delivered days: {delivered_days}."
#                     ),
#                 )
                
                
       
            
#             try:
#                 send_milk_bill_email(bill)

#                 bill.email_sent = True
#                 bill.email_sent_at = timezone.now()

#                 bill.save(
#                     update_fields=[
#                         "email_sent",
#                         "email_sent_at",
#                         "updated_at",
#                     ]
#                 )

#                 self.stdout.write(
#                     self.style.SUCCESS(
#                         f"Email sent to {subscription.user.email}"
#                     )
#                 )

#             except Exception as e:

#                 self.stdout.write(
#                     self.style.ERROR(
#                         f"Bill created but email failed for "
#                         f"{subscription.subscription_number}: {e}"
#                     )
#                 )

#             generated_count += 1

#             customer_name = (
#                 subscription.user.get_full_name()
#                 if hasattr(
#                     subscription.user,
#                     "get_full_name",
#                 )
#                 else subscription.user.email
#             )

#             self.stdout.write(
#                 self.style.SUCCESS(
#                     f"Bill generated | "
#                     f"{subscription.subscription_number} | "
#                     f"{customer_name} | "
#                     f"Rs. {bill.total_amount} | "
#                     f"{delivered_days} days"
#                 )
#             )

#         # --------------------------------------------------
#         # Summary
#         # --------------------------------------------------

#         self.stdout.write("")
#         self.stdout.write(
#             self.style.SUCCESS(
#                 "Milk bill generation completed."
#             )
#         )

#         self.stdout.write(
#             f"Generated: {generated_count}"
#         )

#         self.stdout.write(
#             f"Already existed: {skipped_count}"
#         )

#         self.stdout.write(
#             f"No delivered milk: {zero_bill_count}"
#         )








from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from rdf_app.models import (
    MilkSubscription,
    MilkDelivery,
    MilkBill,
)

from rdf_app.utils import send_milk_bill_email


class Command(BaseCommand):
    help = "Generate monthly milk bills from delivered milk records."

    # ============================================================
    # ARGUMENTS
    # ============================================================

    def add_arguments(self, parser):

        parser.add_argument(
            "--month",
            type=int,
            help=(
                "Billing month (1-12). "
                "Defaults to previous month."
            ),
        )

        parser.add_argument(
            "--year",
            type=int,
            help=(
                "Billing year. "
                "Defaults to previous month year."
            ),
        )

    # ============================================================
    # COMMAND
    # ============================================================

    def handle(self, *args, **options):

        today = timezone.localdate()

        # ========================================================
        # 1. DETERMINE BILLING PERIOD
        # ========================================================

        month_option = options.get("month")
        year_option = options.get("year")

        # Require month and year together
        if bool(month_option) != bool(year_option):

            self.stdout.write(
                self.style.ERROR(
                    "Please provide both --month and --year together."
                )
            )

            return

        if month_option and year_option:

            billing_month = month_option
            billing_year = year_option

            if billing_month < 1 or billing_month > 12:

                self.stdout.write(
                    self.style.ERROR(
                        "Month must be between 1 and 12."
                    )
                )

                return

            if billing_year < 2000:

                self.stdout.write(
                    self.style.ERROR(
                        "Invalid billing year."
                    )
                )

                return

        else:

            # Default to previous month
            first_day_current_month = today.replace(
                day=1
            )

            previous_month_last_day = (
                first_day_current_month
                - timedelta(days=1)
            )

            billing_month = (
                previous_month_last_day.month
            )

            billing_year = (
                previous_month_last_day.year
            )

        # ========================================================
        # 2. BILLING PERIOD DATES
        # ========================================================

        first_day = date(
            billing_year,
            billing_month,
            1,
        )

        last_day = date(
            billing_year,
            billing_month,
            monthrange(
                billing_year,
                billing_month,
            )[1],
        )

        self.stdout.write("")

        self.stdout.write(
            f"Generating milk bills for "
            f"{billing_month:02d}/{billing_year}"
        )

        self.stdout.write(
            f"Period: {first_day} to {last_day}"
        )

        self.stdout.write("")

        # ========================================================
        # 3. SUBSCRIPTIONS
        # ========================================================
        #
        # Current business rule:
        # Generate bills for subscriptions that are currently
        # active and had already started during this billing month.
        #
        # Later, if you want cancelled/expired subscriptions with
        # delivered milk to still receive a final bill, we can
        # change this query to be delivery-based.
        # ========================================================

        subscriptions = (
            MilkSubscription.objects
            .filter(
                status="active",
                start_date__lte=last_day,
            )
            .select_related(
                "user",
                "address",
            )
            .prefetch_related(
                "items",
            )
        )

        # ========================================================
        # COUNTERS
        # ========================================================

        generated_count = 0
        skipped_count = 0
        zero_bill_count = 0

        email_sent_count = 0
        email_failed_count = 0

        # ========================================================
        # 4. PROCESS EACH SUBSCRIPTION
        # ========================================================

        for subscription in subscriptions:

            # ====================================================
            # 5. CHECK FOR EXISTING BILL
            # ====================================================

            existing_bill = (
                MilkBill.objects
                .filter(
                    subscription=subscription,
                    billing_month=billing_month,
                    billing_year=billing_year,
                )
                .first()
            )

            if existing_bill:

                # ------------------------------------------------
                # Retry unsent bill email
                # ------------------------------------------------

                if not existing_bill.email_sent:

                    try:

                        result = send_milk_bill_email(
                            existing_bill
                        )

                        if result.get("success"):

                            existing_bill.email_sent = True

                            existing_bill.email_sent_at = (
                                timezone.now()
                            )

                            existing_bill.save(
                                update_fields=[
                                    "email_sent",
                                    "email_sent_at",
                                    "updated_at",
                                ]
                            )

                            email_sent_count += 1

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Email retry successful: "
                                    f"{subscription.user.email}"
                                )
                            )

                        else:

                            email_failed_count += 1

                            error_message = result.get(
                                "error",
                                "Unknown email error"
                            )

                            self.stdout.write(
                                self.style.WARNING(
                                    f"Email retry failed for "
                                    f"{subscription.subscription_number}: "
                                    f"{error_message}"
                                )
                            )

                    except Exception as exc:

                        email_failed_count += 1

                        self.stdout.write(
                            self.style.ERROR(
                                f"Email retry error for "
                                f"{subscription.subscription_number}: "
                                f"{exc}"
                            )
                        )

                else:

                    self.stdout.write(
                        self.style.WARNING(
                            f"Bill already exists and "
                            f"email already sent: "
                            f"{subscription.subscription_number}"
                        )
                    )

                skipped_count += 1

                continue

            # ====================================================
            # 6. GET DELIVERED MILK
            # ====================================================

            deliveries = (
                MilkDelivery.objects
                .filter(
                    subscription=subscription,
                    delivery_date__range=(
                        first_day,
                        last_day,
                    ),
                    status="delivered",
                )
                .select_related(
                    "subscription_item",
                    "subscription_item__product",
                )
                .order_by(
                    "delivery_date",
                    "id",
                )
            )

            # ====================================================
            # 7. CALCULATE BILL
            # ====================================================

            total_amount = Decimal("0.00")

            delivered_days = 0

            for delivery in deliveries:

                total_amount += (
                    delivery.total_amount
                    or Decimal("0.00")
                )

                delivered_days += 1

            total_amount = total_amount.quantize(
                Decimal("0.01")
            )

            # ====================================================
            # 8. NO DELIVERED MILK
            # ====================================================

            if total_amount <= Decimal("0.00"):

                self.stdout.write(
                    self.style.WARNING(
                        f"No delivered milk: "
                        f"{subscription.subscription_number}"
                    )
                )

                zero_bill_count += 1

                continue

            # ====================================================
            # 9. CREATE BILL
            # ====================================================

            try:

                with transaction.atomic():

                    # Recheck inside the transaction.
                    #
                    # This provides extra protection if the command
                    # is accidentally started twice around the same
                    # time.

                    existing_bill = (
                        MilkBill.objects
                        .filter(
                            subscription=subscription,
                            billing_month=billing_month,
                            billing_year=billing_year,
                        )
                        .first()
                    )

                    if existing_bill:

                        skipped_count += 1

                        self.stdout.write(
                            self.style.WARNING(
                                f"Bill already exists: "
                                f"{subscription.subscription_number}"
                            )
                        )

                        continue

                    bill = MilkBill.objects.create(
                        subscription=subscription,
                        billing_month=billing_month,
                        billing_year=billing_year,

                        total_amount=total_amount,

                        paid_amount=Decimal("0.00"),

                        notes=(
                            f"Generated automatically. "
                            f"Delivered days: "
                            f"{delivered_days}."
                        ),
                    )

            except Exception as exc:

                self.stdout.write(
                    self.style.ERROR(
                        f"Bill creation failed for "
                        f"{subscription.subscription_number}: "
                        f"{exc}"
                    )
                )

                continue

            generated_count += 1

            # ====================================================
            # 10. SEND BILL EMAIL
            # ====================================================

            try:

                result = send_milk_bill_email(
                    bill
                )

                if result.get("success"):

                    bill.email_sent = True

                    bill.email_sent_at = (
                        timezone.now()
                    )

                    bill.save(
                        update_fields=[
                            "email_sent",
                            "email_sent_at",
                            "updated_at",
                        ]
                    )

                    email_sent_count += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Email sent to "
                            f"{subscription.user.email}"
                        )
                    )

                else:

                    email_failed_count += 1

                    error_message = result.get(
                        "error",
                        "Unknown email error"
                    )

                    self.stdout.write(
                        self.style.WARNING(
                            f"Bill created, but email "
                            f"failed for "
                            f"{subscription.subscription_number}: "
                            f"{error_message}"
                        )
                    )

            except Exception as exc:

                email_failed_count += 1

                self.stdout.write(
                    self.style.ERROR(
                        f"Bill created, but email "
                        f"error occurred for "
                        f"{subscription.subscription_number}: "
                        f"{exc}"
                    )
                )

            # ====================================================
            # 11. BILL LOG
            # ====================================================

            customer_name = ""

            if hasattr(
                subscription.user,
                "get_full_name",
            ):

                customer_name = (
                    subscription.user.get_full_name()
                )

            if not customer_name:

                customer_name = (
                    subscription.user.email
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Bill generated | "
                    f"{subscription.subscription_number} | "
                    f"{customer_name} | "
                    f"Rs. {bill.total_amount} | "
                    f"{delivered_days} "
                    f"delivery record(s)"
                )
            )

        # ========================================================
        # 12. SUMMARY
        # ========================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Milk bill generation completed."
            )
        )

        self.stdout.write("")

        self.stdout.write(
            f"Generated: {generated_count}"
        )

        self.stdout.write(
            f"Already existed: {skipped_count}"
        )

        self.stdout.write(
            f"No delivered milk: {zero_bill_count}"
        )

        self.stdout.write(
            f"Emails sent: {email_sent_count}"
        )

        self.stdout.write(
            f"Emails failed: {email_failed_count}"
        )

        self.stdout.write("")