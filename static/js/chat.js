function sendMessage() {
    // Get the user input element and its value
    var userInput = document.getElementById('user-input');
    var message = userInput.value;
    userInput.value = '';  // Clear the input field

    // Display the user's message on the chat
    displayMessage('You: ' + message, 'user');

    // Send the user's message to the server using the fetch API
    fetch('/chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',  // Set the content type for the request
            'X-CSRFToken': getCookie('csrftoken')  // Include CSRF token for security
        },
        body: 'message=' + encodeURIComponent(message)  // Encode the message and include it in the request body
    })
    .then(response => response.json())  // Parse the JSON response from the server
    .then(data => {
        // Display the chatbot's response on the chat
        displayMessage('Chatbot: ' + data.response, 'bot');
    })
    .catch(error => {
        // Display an error message if something goes wrong
        displayMessage('Error: ' + error, 'error');
    });
}

function displayMessage(message, type) {
    var chatContainer = document.getElementById('chat-container');
    var messageElement = document.createElement('p');  // Create a new paragraph element for the message
    messageElement.textContent = message;  // Set the text content of the message

    // Apply different CSS classes based on the message type
    if (type === 'user') {
        messageElement.classList.add('user-message');
    } else if (type === 'bot') {
        messageElement.classList.add('bot-message');
    } else {
        messageElement.classList.add('error');  // Default error class
    }

    chatContainer.appendChild(messageElement);  // Add the message element to the chat container
    chatContainer.scrollTop = chatContainer.scrollHeight;  // Scroll to the bottom of the chat container
}

function getCookie(name) {
    var cookieValue = null;  // Initialize the variable to hold the cookie value
    if (document.cookie && document.cookie !== '') {  // Check if there are cookies
        var cookies = document.cookie.split(';');  // Split the cookies string into individual cookies
        for (var i = 0; i < cookies.length; i++) {  // Loop through the cookies
            var cookie = cookies[i].trim();  // Trim any leading or trailing whitespace
            // Check if the cookie name matches the desired name
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));  // Decode and assign the cookie value
                break;
            }
        }
    }
    return cookieValue;  // Return the cookie value
}
