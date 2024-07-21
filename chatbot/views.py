from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .chatbot_logic import Chatbot


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

            # Get the singleton instance of the Chatbot class
            chatbot = Chatbot.get_instance()

            # Get the chatbot's response to the user's message
            response = chatbot.get_response(user_message)

            # Return the response as a JSON object
            return JsonResponse({'response': response})

        # Handle any exceptions that occur during processing
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # Return an error response if the request method is not POST
    return JsonResponse({'error': 'Invalid request'}, status=400)
