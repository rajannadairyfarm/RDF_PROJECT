from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from rdf_app.models import (
    MilkSubscription,
    MilkSubscriptionItem,
    MilkDelivery,
)


class Command(BaseCommand):
    help = "Generate today's scheduled milk deliveries for active subscriptions."

    def handle(self, *args, **options):

        today = timezone.localdate()

        self.stdout.write(
            f"Generating milk deliveries for {today}"
        )

        subscriptions = (
            MilkSubscription.objects
            .filter(
                status="active",
                start_date__lte=today,
            )
            .select_related(
                "user",
                "address",
            )
            .prefetch_related(
                "items__product",
            )
        )

        created_count = 0
        existing_count = 0
        skipped_count = 0

        for subscription in subscriptions:

            # Subscription has ended
            if (
                subscription.end_date
                and today > subscription.end_date
            ):
                skipped_count += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"Skipped expired subscription: "
                        f"{subscription.subscription_number}"
                    )
                )

                continue

            items = subscription.items.all()

            for item in items:

                # Item has not started yet
                if today < item.start_date:
                    skipped_count += 1
                    continue

                # Item has ended
                if (
                    item.end_date
                    and today > item.end_date
                ):
                    skipped_count += 1
                    continue

                # We currently support daily subscriptions
                if item.frequency != "daily":
                    skipped_count += 1
                    continue

                # Prevent duplicate delivery
                delivery_exists = (
                    MilkDelivery.objects.filter(
                        subscription_item=item,
                        delivery_date=today,
                    ).exists()
                )

                if delivery_exists:

                    existing_count += 1

                    self.stdout.write(
                        self.style.WARNING(
                            f"Already exists: "
                            f"{subscription.subscription_number} "
                            f"- {today}"
                        )
                    )

                    continue
                
                
                
                
                total_amount = (
                    item.price_per_unit
                    * item.quantity
                ).quantize(
                    Decimal("0.01")
                )

                with transaction.atomic():

                    delivery, created = (
                        MilkDelivery.objects.get_or_create(
                            subscription_item=item,
                            delivery_date=today,
                            defaults={
                                "subscription": subscription,
                                "quantity": item.quantity,
                                "unit_price": item.price_per_unit,
                                "total_amount": total_amount,
                                "status": "scheduled",
                            }
                        )
                    )

                if not created:

                    existing_count += 1

                    self.stdout.write(
                        self.style.WARNING(
                            f"Already exists: "
                            f"{subscription.subscription_number} "
                            f"- {today}"
                        )
                    )

                    continue


                created_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created delivery: "
                        f"{subscription.subscription_number} | "
                        f"{item.product.name} | "
                        f"Qty: {item.quantity} | "
                        f"Rs.{total_amount}"
                    )
                )

                # # Calculate delivery amount
                # total_amount = (
                #     item.price_per_unit * item.quantity
                # ).quantize(
                #     Decimal("0.01")
                # )

                # # Create delivery
                # with transaction.atomic():

                #     MilkDelivery.objects.create(
                #         subscription=subscription,
                #         subscription_item=item,
                #         delivery_date=today,
                #         quantity=item.quantity,
                #         unit_price=item.price_per_unit,
                #         total_amount=total_amount,
                #         status="scheduled",
                #     )

                # created_count += 1

                # self.stdout.write(
                #     self.style.SUCCESS(
                #         f"Created delivery: "
                #         f"{subscription.subscription_number} | "
                #         f"{item.product.name} | "
                #         f"Qty: {item.quantity} | "
                #         f"Rs.{total_amount}"
                #     )
                # )

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Milk delivery generation completed."
            )
        )

        self.stdout.write(
            f"Created: {created_count}"
        )

        self.stdout.write(
            f"Already existed: {existing_count}"
        )

        self.stdout.write(
            f"Skipped: {skipped_count}"
        )