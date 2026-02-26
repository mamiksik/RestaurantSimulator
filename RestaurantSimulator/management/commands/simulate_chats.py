from django.core.management import BaseCommand
from RestaurantSimulator.simulator.tasks import step4_waiter


class Command(BaseCommand):
    help = "Simulate chat threads for testing purposes."

    def handle(self, *args, **options):
        step4_waiter()
