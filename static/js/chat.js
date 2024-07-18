function sendMessage() {
    var userInput = document.getElementById('user-input');
    var message = userInput.value;
    userInput.value = '';

    displayMessage('You: ' + message, 'user');

    fetch('/chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: 'message=' + encodeURIComponent(message)
    })
    .then(response => response.json())
    .then(data => {
        displayMessage('Chatbot: ' + data.response, 'bot');
    })
    .catch(error => {
        displayMessage('Error: ' + error, 'error');
    });
}

function displayMessage(message, type) {
    var chatContainer = document.getElementById('chat-container');
    var messageElement = document.createElement('p');
    messageElement.textContent = message;

    // Apply different classes based on message type
    if (type === 'user') {
        messageElement.classList.add('user-message');
    } else if (type === 'bot') {
        messageElement.classList.add('bot-message');
    } else {
        messageElement.classList.add('error'); // Default error class
    }

    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
