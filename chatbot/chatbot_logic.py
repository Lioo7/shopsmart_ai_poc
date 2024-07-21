from sentence_transformers import SentenceTransformer
import faiss
from .models import Product
from django.core.exceptions import ObjectDoesNotExist


class Chatbot:
    _instance = None

    @classmethod
    def get_instance(cls):
        # Singleton pattern to ensure only one instance of the Chatbot is created
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # Initialize the sentence transformer model
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.products = []
        self.product_embeddings = None
        self.index = None
        self.dimension = None
        self.refresh_index()

    def refresh_index(self):
        try:
            # Fetch all products from the database
            self.products = list(Product.objects.all())
            if not self.products:
                raise ObjectDoesNotExist("No products found in the database.")

            # Generate embeddings for product descriptions
            product_descriptions = [p.description for p in self.products]
            self.product_embeddings = self.model.encode(product_descriptions)

            # Get the dimension of the embeddings (number of features in each embedding vector)
            self.dimension = self.product_embeddings.shape[1]
            self.index = faiss.IndexFlatL2(self.dimension)
            # Add embeddings to the FAISS index
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
            # Encode the query into an embedding
            query_embedding = self.model.encode([query])
            k = min(len(self.products), 10)  # Get top 10 products initially
            distances, indices = self.index.search(query_embedding.astype('float32'), k)

            # Extract price range from the query if specified
            price_range = self.extract_price_range(query)

            response = "Based on your query, here are some recommendations:\n\n"
            recommended_products = []

            # Filter products by price range and avoid duplicates
            for idx in indices[0]:
                product = self.products[idx]
                if self.product_matches_criteria(product, price_range) and product not in recommended_products:
                    recommended_products.append(product)

                if len(recommended_products) == 3:
                    break

            if not recommended_products:
                response += "I'm sorry, but I couldn't find any products matching your criteria. "
                response += "Here are our closest matches:\n\n"
                recommended_products = list(set(self.products[:3]))

            # Format the response with product details
            for i, product in enumerate(recommended_products, 1):
                response += f"{i}. {product.name}\n"
                response += f"   - Color: {product.color}\n"
                response += f"   - Price: ${product.price:.2f}\n"
                response += f"   - Description: {product.description}\n\n"

            return response
        except Exception as e:
            return f"I'm sorry, but I encountered an error while processing your request: {str(e)}"

    def extract_price_range(self, query):
        # Extracts price range from the query if it contains phrases like "under $200"
        if "under $" in query.lower():
            try:
                max_price = float(query.lower().split("under $")[1].split()[0])
                return (0, max_price)
            except:
                pass
        return None

    def product_matches_criteria(self, product, price_range):
        # Checks if the product's price falls within the specified price range
        if price_range:
            return price_range[0] <= product.price <= price_range[1]
        return True
