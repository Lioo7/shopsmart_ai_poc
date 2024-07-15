from django.core.management.base import BaseCommand
from chatbot.models import Product


class Command(BaseCommand):
    help = 'Initialize product data'

    def handle(self, *args, **kwargs):
        products = [
            {"name": "Gamer Pro Chair", "description": "High-end gaming chair with lumbar support", "color": "black", "price": 299.99},
            {"name": "Ergonomic Office Chair", "description": "Comfortable chair for long work hours", "color": "gray", "price": 199.99},
            {"name": "Budget Gaming Seat", "description": "Affordable chair for casual gamers", "color": "red", "price": 149.99},
            {"name": "Executive Leather Chair", "description": "Luxurious leather chair for executives", "color": "brown", "price": 399.99},
            {"name": "Mesh Back Chair", "description": "Breathable mesh chair for hot climates", "color": "blue", "price": 179.99},
            {"name": "Foldable Gaming Chair", "description": "Compact gaming chair for small spaces", "color": "green", "price": 129.99},
            {"name": "Rocking Gaming Chair", "description": "Gaming chair with rocking function", "color": "purple", "price": 249.99},
            {"name": "Racing Style Gaming Chair", "description": "Sleek racing-inspired gaming chair", "color": "white", "price": 219.99},
        ]

        for product in products:
            Product.objects.create(**product)

        self.stdout.write(self.style.SUCCESS('Successfully initialized product data'))
