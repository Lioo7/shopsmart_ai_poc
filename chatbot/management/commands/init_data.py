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
            {"name": "Standing Desk", "description": "Adjustable height desk for ergonomic work", "color": "black", "price": 349.99},
            {"name": "L-Shaped Computer Desk", "description": "Spacious corner desk for multi-monitor setups", "color": "oak", "price": 189.99},
            {"name": "Floating Wall Desk", "description": "Space-saving desk that mounts to the wall", "color": "white", "price": 129.99},
            {"name": "Gaming Mouse", "description": "High-precision mouse with programmable buttons", "color": "black", "price": 59.99},
            {"name": "Mechanical Keyboard", "description": "Tactile keyboard with customizable RGB lighting", "color": "black", "price": 89.99},
            {"name": "Ultra-wide Monitor", "description": "34-inch curved display for immersive viewing", "color": "black", "price": 499.99},
            {"name": "Noise-cancelling Headphones", "description": "Over-ear headphones for focused work or gaming", "color": "silver", "price": 249.99},
            {"name": "Ergonomic Mouse Pad", "description": "Wrist-rest mouse pad for comfortable use", "color": "black", "price": 19.99},
        ]

        for product in products:
            Product.objects.create(**product)

        self.stdout.write(self.style.SUCCESS('Successfully initialized product data'))
