from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .chatbot_logic import RAGChatbot
import logging

logger = logging.getLogger(__name__)


# Renders the index HTML page
def index(request):
    return render(request, 'chatbot/index.html')


# Exempting the chat view from CSRF verification
@csrf_exempt
def chat(request):
    # Check if the request method is POST
    if request.method == 'POST':
        try:
            # Retrieve the user's message from the POST data
            user_message = request.POST.get('message', '')
            logger.info(f"Received message: {user_message}")
            chatbot = RAGChatbot.get_instance()
            response = chatbot.get_response(user_message)
            logger.info(f"Response from chatbot: {response}")
            if not response:
                response = "I apologize, but I couldn't generate a response. Please try again."
            return JsonResponse({'response': response})

        # Handle any exceptions that occur during processing
        except Exception as e:
            logger.error(f"Error in chat view: {str(e)}", exc_info=True)
            return JsonResponse({'error': f"An error occurred: {str(e)}"}, status=500)
    # Return an error response if the request method is not POST
    return JsonResponse({'error': 'Invalid request'}, status=400)
