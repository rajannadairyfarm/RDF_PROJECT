from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from rdf_app.models import (
    MilkSubscription,
    MilkSubscriptionItem,
    MilkDelivery,
    MilkBill,
)


class Command(BaseCommand):

    help = "Check the health of the Rajanna Dairy Farm milk system"

    def handle(self, *args, **options):

        today = timezone.localdate()

        # ==========================================================
        # HEADER
        # ==========================================================

        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write(
            "RAJANNA DAIRY FARM - MILK SYSTEM HEALTH"
        )
        self.stdout.write("=" * 70)

        self.stdout.write(
            f"Date: {today}"
        )

        problems = 0

        # ==========================================================
        # 1. SUBSCRIPTION HEALTH
        # ==========================================================

        active_subscriptions = (
            MilkSubscription.objects
            .filter(
                status="active",
                start_date__lte=today,
            )
            .filter(
                models.Q(end_date__isnull=True)
                | models.Q(end_date__gte=today)
            )
            .count()
        )

        pending_subscriptions = MilkSubscription.objects.filter(
            status="pending"
        ).count()

        paused_subscriptions = MilkSubscription.objects.filter(
            status="paused"
        ).count()

        cancelled_subscriptions = MilkSubscription.objects.filter(
            status="cancelled"
        ).count()

        expired_subscriptions = MilkSubscription.objects.filter(
            status="expired"
        ).count()

        self.stdout.write("")
        self.stdout.write("SUBSCRIPTION HEALTH")
        self.stdout.write("-" * 70)

        self.stdout.write(
            f"Active       : {active_subscriptions}"
        )

        self.stdout.write(
            f"Pending      : {pending_subscriptions}"
        )

        self.stdout.write(
            f"Paused       : {paused_subscriptions}"
        )

        self.stdout.write(
            f"Cancelled    : {cancelled_subscriptions}"
        )

        self.stdout.write(
            f"Expired      : {expired_subscriptions}"
        )

        # ==========================================================
        # 2. EXPECTED DAILY DELIVERIES
        # ==========================================================

        eligible_items = (
            MilkSubscriptionItem.objects
            .filter(
                subscription__status="active",
                subscription__start_date__lte=today,
                frequency="daily",
                start_date__lte=today,
            )
            .filter(
                models.Q(subscription__end_date__isnull=True)
                | models.Q(subscription__end_date__gte=today)
            )
            .filter(
                models.Q(end_date__isnull=True)
                | models.Q(end_date__gte=today)
            )
        )

        expected_deliveries = eligible_items.count()

        # ==========================================================
        # 3. TODAY'S DELIVERY HEALTH
        # ==========================================================

        today_deliveries = MilkDelivery.objects.filter(
            delivery_date=today
        )

        actual_deliveries = today_deliveries.count()

        scheduled_today = today_deliveries.filter(
            status="scheduled"
        ).count()

        delivered_today = today_deliveries.filter(
            status="delivered"
        ).count()

        missed_today = today_deliveries.filter(
            status="missed"
        ).count()

        skipped_today = today_deliveries.filter(
            status="skipped"
        ).count()

        paused_today = today_deliveries.filter(
            status="paused"
        ).count()

        cancelled_today = today_deliveries.filter(
            status="cancelled"
        ).count()

        missing_deliveries = max(
            0,
            expected_deliveries - actual_deliveries,
        )

        self.stdout.write("")
        self.stdout.write("TODAY'S DELIVERY HEALTH")
        self.stdout.write("-" * 70)

        self.stdout.write(
            f"Expected Deliveries : {expected_deliveries}"
        )

        self.stdout.write(
            f"Actual Deliveries   : {actual_deliveries}"
        )

        self.stdout.write(
            f"Missing Deliveries  : {missing_deliveries}"
        )

        self.stdout.write(
            f"Scheduled           : {scheduled_today}"
        )

        self.stdout.write(
            f"Delivered           : {delivered_today}"
        )

        self.stdout.write(
            f"Missed              : {missed_today}"
        )

        self.stdout.write(
            f"Skipped             : {skipped_today}"
        )

        self.stdout.write(
            f"Paused              : {paused_today}"
        )

        self.stdout.write(
            f"Cancelled           : {cancelled_today}"
        )

        # ==========================================================
        # 4. TODAY'S MILK QUANTITY & VALUE
        # ==========================================================

        today_quantity = (
            today_deliveries
            .filter(
                status="delivered"
            )
            .aggregate(
                total=Sum("quantity")
            )["total"]
            or Decimal("0")
        )

        today_delivery_value = (
            today_deliveries
            .filter(
                status="delivered"
            )
            .aggregate(
                total=Sum("total_amount")
            )["total"]
            or Decimal("0.00")
        )

        self.stdout.write("")
        self.stdout.write("TODAY'S DELIVERED MILK")
        self.stdout.write("-" * 70)

        self.stdout.write(
            f"Quantity            : {today_quantity}"
        )

        self.stdout.write(
            f"Delivery Value      : INR {today_delivery_value}"
        )

        # ==========================================================
        # 5. CURRENT MONTH BILL HEALTH
        # ==========================================================

        current_month = today.month
        current_year = today.year

        bills = MilkBill.objects.filter(
            billing_month=current_month,
            billing_year=current_year,
        )

        total_bills = bills.count()

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

        paid_bills = bills.filter(
            status="paid"
        ).count()

        partial_bills = bills.filter(
            status="partial"
        ).count()

        pending_bills = bills.filter(
            status="pending"
        ).count()

        unsent_emails = bills.filter(
            email_sent=False
        ).count()

        self.stdout.write("")
        self.stdout.write(
            f"BILL HEALTH - {current_month:02d}/{current_year}"
        )
        self.stdout.write("-" * 70)

        self.stdout.write(
            f"Total Bills      : {total_bills}"
        )

        self.stdout.write(
            f"Total Billed     : INR {total_billed}"
        )

        self.stdout.write(
            f"Collected        : INR {total_collected}"
        )

        self.stdout.write(
            f"Pending          : INR {total_pending}"
        )

        self.stdout.write(
            f"Paid Bills       : {paid_bills}"
        )

        self.stdout.write(
            f"Partial Bills    : {partial_bills}"
        )

        self.stdout.write(
            f"Pending Bills    : {pending_bills}"
        )

        self.stdout.write(
            f"Unsent Emails    : {unsent_emails}"
        )

        # ==========================================================
        # 6. SYSTEM WARNINGS
        # ==========================================================

        self.stdout.write("")
        self.stdout.write("SYSTEM CHECK")
        self.stdout.write("-" * 70)

        # ----------------------------------------------------------
        # Missing deliveries
        # ----------------------------------------------------------

        if missing_deliveries > 0:

            self.stdout.write(
                self.style.WARNING(
                    f"WARNING: {missing_deliveries} expected "
                    "delivery(s) have not been generated."
                )
            )

            problems += 1

        else:

            self.stdout.write(
                self.style.SUCCESS(
                    "OK: All expected deliveries have been generated."
                )
            )

        # ----------------------------------------------------------
        # Unsent bill emails
        # ----------------------------------------------------------

        if unsent_emails > 0:

            self.stdout.write(
                self.style.WARNING(
                    f"WARNING: {unsent_emails} bill email(s) "
                    "are not marked as sent."
                )
            )

            problems += 1

        else:

            self.stdout.write(
                self.style.SUCCESS(
                    "OK: All current-month bill emails are sent."
                )
            )

        # ----------------------------------------------------------
        # Pending cash collection
        # ----------------------------------------------------------

        if total_pending > Decimal("0.00"):

            self.stdout.write(
                self.style.WARNING(
                    f"INFO: INR {total_pending} is pending "
                    "for the current month."
                )
            )

        else:

            self.stdout.write(
                self.style.SUCCESS(
                    "OK: No pending cash collection for current month."
                )
            )

        # ==========================================================
        # 7. FINAL HEALTH STATUS
        # ==========================================================

        self.stdout.write("")
        self.stdout.write("=" * 70)

        if problems == 0:

            self.stdout.write(
                self.style.SUCCESS(
                    "SYSTEM HEALTH: OK"
                )
            )

        else:

            self.stdout.write(
                self.style.ERROR(
                    f"SYSTEM HEALTH: {problems} issue(s) detected."
                )
            )

        self.stdout.write("=" * 70)
        self.stdout.write("")