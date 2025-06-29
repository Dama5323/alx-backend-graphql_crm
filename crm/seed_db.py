from django.core.management.base import BaseCommand
from crm.models import Customer, Product, Order
from django.utils.timezone import now
import random

class Command(BaseCommand):
    help = "Seed the database with sample data"

    def handle(self, *args, **kwargs):
        # Clear existing data
        Order.objects.all().delete()
        Customer.objects.all().delete()
        Product.objects.all().delete()

        self.stdout.write(self.style.NOTICE("Cleared existing data."))

        # Create Customers
        customers_data = [
            {"name": "Alice Johnson", "email": "alice@example.com", "phone": "+1234567890"},
            {"name": "Bob Smith", "email": "bob@example.com", "phone": "123-456-7890"},
            {"name": "Carol White", "email": "carol@example.com", "phone": None},
        ]
        customers = []
        for data in customers_data:
            customer = Customer.objects.create(**data)
            customers.append(customer)
            self.stdout.write(self.style.SUCCESS(f"Created customer: {customer.name}"))

        # Create Products
        products_data = [
            {"name": "Laptop", "price": 999.99, "stock": 10},
            {"name": "Mouse", "price": 19.99, "stock": 50},
            {"name": "Keyboard", "price": 49.99, "stock": 30},
        ]
        products = []
        for data in products_data:
            product = Product.objects.create(**data)
            products.append(product)
            self.stdout.write(self.style.SUCCESS(f"Created product: {product.name}"))

        # Create Orders
        for i in range(3):
            customer = random.choice(customers)
            selected_products = random.sample(products, k=2)
            total = sum([p.price for p in selected_products])
            order = Order.objects.create(customer=customer, total_amount=total, order_date=now())
            order.products.set(selected_products)
            order.save()
            self.stdout.write(self.style.SUCCESS(f"Created order #{order.id} for {customer.name}"))

        self.stdout.write(self.style.SUCCESS("Database seeding complete."))
