from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .chatbot_logic import Chatbot


def index(request):
    return render(request, 'chatbot/index.html')


@csrf_exempt
def chat(request):
    if request.method == 'POST':
        try:
            user_message = request.POST.get('message', '')
            chatbot = Chatbot.get_instance()
            response = chatbot.get_response(user_message)
            return JsonResponse({'response': response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)
