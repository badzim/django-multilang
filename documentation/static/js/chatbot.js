// chatbot.js
document.addEventListener('DOMContentLoaded', function () {
    const chatbotButton = document.getElementById('chatbot-toggle');
    const chatContainer = document.getElementById('chat-container');
    const chatbotForm = document.getElementById('chat-form');
    const chatbotInput = document.getElementById('chat-input');
    const chatbotMessages = document.getElementById('chat-log');
    const sendButton = document.getElementById('send-button'); // Ajouter une référence au bouton de soumission

    // Ajouter le bouton de nettoyage
    const clearButton = document.createElement('button');
    clearButton.id = 'clear-button';
    clearButton.className = 'btn btn-danger';
    clearButton.textContent = clearText;
    chatContainer.appendChild(clearButton);

    // Fonction pour sauvegarder les messages dans le localStorage
    function saveMessages() {
        const messages = chatbotMessages.innerHTML;
        localStorage.setItem('chatbotMessages', messages);
    }

    // Fonction pour restaurer les messages du localStorage
    function loadMessages() {
        const messages = localStorage.getItem('chatbotMessages');
        if (messages) {
            chatbotMessages.innerHTML = messages;
            chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        }
    }

    // Fonction pour effacer les messages
    function clearMessages() {
        chatbotMessages.innerHTML = '';
        localStorage.removeItem('chatbotMessages');
    }

    // Restaurer les messages au chargement de la page
    loadMessages();

    chatbotButton.addEventListener('click', function () {
        if (chatContainer.style.display === 'none' || chatContainer.style.display === '') {
            chatContainer.style.display = 'block';
            chatbotButton.innerText = 'X'; // Change button text to "X" when open
        } else {
            chatContainer.style.display = 'none';
            chatbotButton.innerText = chatbotText; // Use the translated chatbot text
        }
    });

    chatbotForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const message = chatbotInput.value.trim();
        if (message) {
            // Désactiver le bouton de soumission
            sendButton.disabled = true;

            // Afficher le message de l'utilisateur
            const userMessage = document.createElement('div');
            userMessage.textContent = message;
            userMessage.className = 'user-message alert alert-primary';
            chatbotMessages.appendChild(userMessage);
            saveMessages(); // Sauvegarder les messages

            // Afficher le message de chargement du chatbot
            const botLoadingMessage = document.createElement('div');
            botLoadingMessage.textContent = '...';
            botLoadingMessage.className = 'bot-message alert alert-secondary';
            chatbotMessages.appendChild(botLoadingMessage);
            saveMessages(); // Sauvegarder les messages

            // Envoyer la requête au serveur
            fetch(chatbotUrl, {  // Utilisation de la variable chatbotUrl
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ question: message })
            })
            .then(response => response.json())
            .then(data => {
                // Supprimer le message de chargement du chatbot
                chatbotMessages.removeChild(botLoadingMessage);

                // Afficher la réponse du chatbot
                const botMessage = document.createElement('div');
                const md = window.markdownit();
                botMessage.innerHTML = md.render(data.answer);
                botMessage.className = 'bot-message alert alert-secondary';
                chatbotMessages.appendChild(botMessage);
                chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
                saveMessages(); // Sauvegarder les messages

                // Réactiver le bouton de soumission
                sendButton.disabled = false;
            })
            .catch(error => {
                console.error('Error:', error);
                chatbotMessages.removeChild(botLoadingMessage);
                saveMessages(); // Sauvegarder les messages en cas d'erreur
                // Réactiver le bouton de soumission en cas d'erreur
                sendButton.disabled = false;
            });

            chatbotInput.value = '';
        }
    });

    clearButton.addEventListener('click', function () {
        clearMessages();
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
