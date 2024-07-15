from django.shortcuts import render
from django.http import JsonResponse
from .chatbot_logic import chatbot


def index(request):
    return render(request, 'chatbot/index.html')


def chat(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        response = chatbot.get_response(user_message)
        return JsonResponse({'response': response})
    return JsonResponse({'error': 'Invalid request'}, status=400)
