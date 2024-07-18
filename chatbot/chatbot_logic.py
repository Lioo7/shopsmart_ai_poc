from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from .models import Product
from django.core.exceptions import ObjectDoesNotExist


class Chatbot:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.products = []
        self.product_embeddings = None
        self.index = None
        self.dimension = None
        self.refresh_index()

    def refresh_index(self):
        try:
            self.products = list(Product.objects.all())
            if not self.products:
                raise ObjectDoesNotExist("No products found in the database.")
            
            product_descriptions = [p.description for p in self.products]
            self.product_embeddings = self.model.encode(product_descriptions)

            self.dimension = self.product_embeddings.shape[1]
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index.add(self.product_embeddings.astype('float32'))
            print("Index refreshed successfully.")
        except ObjectDoesNotExist as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Error refreshing index: {str(e)}")

    def get_response(self, query):
        if self.index is None:
            self.refresh_index()
        try:
            query_embedding = self.model.encode([query])
            k = min(len(self.products), 10)  # Get top 10 products initially
            distances, indices = self.index.search(query_embedding.astype('float32'), k)

            # Extract price range from query
            price_range = self.extract_price_range(query)

            response = "Based on your query, here are some recommendations:\n\n"
            recommended_products = []

            for idx in indices[0]:
                product = self.products[idx]
                if self.product_matches_criteria(product, price_range) and product not in recommended_products:
                    recommended_products.append(product)

                if len(recommended_products) == 3:
                    break

            if not recommended_products:
                response += "I'm sorry, but I couldn't find any products matching your criteria. "
                response += "Here are our closest matches:\n\n"
                recommended_products = list(set(self.products[:3]))  # Use set to remove duplicates

            for i, product in enumerate(recommended_products, 1):
                response += f"{i}. {product.name}\n"
                response += f"   - Color: {product.color}\n"
                response += f"   - Price: ${product.price:.2f}\n"
                response += f"   - Description: {product.description}\n\n"

            return response
        except Exception as e:
            return f"I'm sorry, but I encountered an error while processing your request: {str(e)}"

    def extract_price_range(self, query):
        if "under $" in query.lower():
            try:
                max_price = float(query.lower().split("under $")[1].split()[0])
                return (0, max_price)
            except:
                pass
        return None

    def product_matches_criteria(self, product, price_range):
        if price_range:
            return price_range[0] <= product.price <= price_range[1]
        return True
