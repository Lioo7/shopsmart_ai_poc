from sentence_transformers import SentenceTransformer
import faiss
from .models import Product
from django.core.exceptions import ObjectDoesNotExist
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import re


class RAGChatbot:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.retriever_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.products = []
        self.product_embeddings = None
        self.index = None
        self.dimension = None

        # Initialize language model for generation
        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
        self.language_model = AutoModelForCausalLM.from_pretrained("gpt2")

        # Add padding token to tokenizer
        self.tokenizer.pad_token = self.tokenizer.eos_token

        self.refresh_index()

    def refresh_index(self):
        try:
            self.products = list(Product.objects.all())
            if not self.products:
                raise ObjectDoesNotExist("No products found in the database.")

            product_descriptions = [p.description for p in self.products]
            self.product_embeddings = self.retriever_model.encode(product_descriptions)

            self.dimension = self.product_embeddings.shape[1]
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index.add(self.product_embeddings.astype('float32'))
            print("Index refreshed successfully.")
        except ObjectDoesNotExist as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Error refreshing index: {str(e)}")

    def extract_price_range(self, query):
        patterns = [
            r'under \$(\d+)',
            r'less than \$(\d+)',
            r'between \$(\d+) and \$(\d+)',
            r'\$(\d+)\s*-\s*\$(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                if len(match.groups()) == 1:
                    return (0, float(match.group(1)))
                elif len(match.groups()) == 2:
                    return (float(match.group(1)), float(match.group(2)))
        return None

    def extract_color(self, query):
        colors = ['red', 'blue', 'green', 'yellow', 'black', 'white', 'purple', 'orange', 'pink', 'brown', 'gray']
        for color in colors:
            if color in query.lower():
                return color
        return None

    def product_matches_criteria(self, product, price_range, color):
        if price_range and not (price_range[0] <= product.price <= price_range[1]):
            return False
        if color and product.color.lower() != color:
            return False
        return True

    def format_product_info(self, products):
        context = ""
        for i, product in enumerate(products, 1):
            context += f"{i}. {product.name}\n"
            context += f"   - Color: {product.color}\n"
            context += f"   - Price: ${product.price:.2f}\n"
            context += f"   - Description: {product.description}\n\n"
        return context

    def generate_response(self, query, context):
        prompt = f"""User Query: {query}

    Product Information:
    {context}

    Chatbot: Based on your query for a blue gaming chair in the price range of $150-$200, here are my recommendations:

    1. """
        
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt")
        attention_mask = torch.ones(input_ids.shape, dtype=torch.long)
        
        with torch.no_grad():
            output = self.language_model.generate(
                input_ids,
                attention_mask=attention_mask,
                max_length=500,  # Increased max length
                num_return_sequences=1,
                no_repeat_ngram_size=3,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        response = generated_text.split("Chatbot:")[-1].strip()
        
        # If the generated response is too short or generic, provide a fallback response
        if len(response.split()) < 20 or "http" in response:
            fallback_response = f"Based on your query for a blue gaming chair in the price range of $150-$200, I recommend the following product:\n\n{context}"
            return fallback_response
        
        return response

    def get_response(self, query):
        if self.index is None:
            self.refresh_index()
        try:
            print(f"Processing query: {query}")
            query_embedding = self.retriever_model.encode([query])
            k = min(len(self.products), 10)
            distances, indices = self.index.search(query_embedding.astype('float32'), k)

            price_range = self.extract_price_range(query)
            color = self.extract_color(query)
            print(f"Extracted price range: {price_range}, color: {color}")

            recommended_products = []
            for idx in indices[0]:
                product = self.products[idx]
                if self.product_matches_criteria(product, price_range, color) and product not in recommended_products:
                    recommended_products.append(product)
                if len(recommended_products) == 3:
                    break

            print(f"Number of recommended products: {len(recommended_products)}")

            if not recommended_products:
                context = "I'm sorry, but I couldn't find any products exactly matching your criteria. Here are our closest matches:\n\n"
                recommended_products = list(set(self.products[:3]))
            else:
                if price_range and color:
                    context = f"Based on your query for a {color} gaming chair in the price range of ${price_range[0]}-${price_range[1]}, here are some recommendations:\n\n"
                elif color:
                    context = f"Based on your query for a {color} gaming chair, here are some recommendations:\n\n"
                elif price_range:
                    context = f"Based on your query for a gaming chair in the price range of ${price_range[0]}-${price_range[1]}, here are some recommendations:\n\n"
                else:
                    context = "Based on your query, here are some recommendations:\n\n"

            context += self.format_product_info(recommended_products)
            print(f"Generated context: {context}")

            try:
                generated_response = self.generate_response(query, context)
                print(f"Generated response: {generated_response}")
            except Exception as e:
                print(f"Error in generate_response: {str(e)}")
                generated_response = context  # Fallback to using the context as the response

            return generated_response

        except Exception as e:
            print(f"Error in get_response: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"I apologize, but I encountered an error while processing your request. Please try again later. Error: {str(e)}"
        