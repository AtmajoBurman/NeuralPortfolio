document.addEventListener('DOMContentLoaded', () => {
    const fab = document.querySelector('.ai-chatbot-fab');
    const windowEl = document.querySelector('.chatbot-window');
    const msgEl = document.querySelector('.ai-chatbot-message');
    const closeBtn = document.querySelector('.chatbot-close');
    const inputField = document.querySelector('.chatbot-input');
    const sendBtn = document.querySelector('.chatbot-send');
    const messagesContainer = document.querySelector('.chatbot-messages');

    let isOpen = false;

    // Toggle Chat Window
    function toggleChat() {
        isOpen = !isOpen;
        if (isOpen) {
            windowEl.classList.add('active');
            msgEl.classList.add('hidden');
            fab.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"></path></svg>';
            setTimeout(() => inputField.focus(), 300);
        } else {
            windowEl.classList.remove('active');
            msgEl.classList.remove('hidden');
            fab.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path><path d="M9 10h.01"></path><path d="M15 10h.01"></path><path d="M12 10h.01"></path></svg>';
        }
    }

    fab.addEventListener('click', toggleChat);
    closeBtn.addEventListener('click', toggleChat);

    // Initial greeting
    const addBotMessage = (text) => {
        const bubble = document.createElement('div');
        bubble.className = 'chat-bubble bot';
        bubble.textContent = text;
        messagesContainer.appendChild(bubble);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    };

    const addUserMessage = (text) => {
        const bubble = document.createElement('div');
        bubble.className = 'chat-bubble user';
        bubble.textContent = text;
        messagesContainer.appendChild(bubble);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    };

    const showTyping = () => {
        const typing = document.createElement('div');
        typing.className = 'chat-bubble bot typing-wrapper';
        typing.innerHTML = '<div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>';
        messagesContainer.appendChild(typing);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return typing;
    };

    // Initialize with greeting
    setTimeout(() => {
        addBotMessage("Hi! I'm Riku, your AI assistant. How can I help you explore this portfolio today?");
    }, 500);

    // Send Message Logic
    const sendMessage = async () => {
        const text = inputField.value.trim();
        if (!text) return;

        addUserMessage(text);
        inputField.value = '';
        const typingIndicator = showTyping();

        try {
            const API_BASE_URL = import.meta.env?.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
            // Add a timestamp query param to bypass the browser's cached CORS preflight failure
            const response = await fetch(`${API_BASE_URL}/api/chatbot?t=${Date.now()}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: text })
            });

            const data = await response.json();
            typingIndicator.remove();
            
            if (data.reply) {
                addBotMessage(data.reply);
            } else {
                addBotMessage("I'm so sorry, but I'm currently having trouble connecting to my database or processing your request. Please try again later, or reach out to the admin directly via LinkedIn or email!");
            }
        } catch (error) {
            console.error('Chat error:', error);
            typingIndicator.remove();
            addBotMessage("I'm so sorry, but I'm currently having trouble connecting to my database or processing your request. Please try again later, or reach out to the admin directly via LinkedIn or email!");
        }
    };

    sendBtn.addEventListener('click', sendMessage);
    inputField.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
