from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from .models import Product


class Chatbot:
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.products = list(Product.objects.all())
        self.product_embeddings = self.model.encode([p.description for p in self.products])

        self.dimension = self.product_embeddings.shape[1]
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(self.product_embeddings.astype('float32'))

    def get_response(self, query):
        query_embedding = self.model.encode([query])
        k = 3  # number of results to return
        distances, indices = self.index.search(query_embedding.astype('float32'), k)

        response = "Based on your query, here are some recommendations:\n\n"
        for idx in indices[0]:
            product = self.products[idx]
            response += f"- {product.name} (Color: {product.color}, Price: ${product.price})\n"

        return response


chatbot = Chatbot()
