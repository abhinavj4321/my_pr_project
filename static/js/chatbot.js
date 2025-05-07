// Chatbot functionality
class Chatbot {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.currentFaqId = null;
        this.currentQuestion = "";
        this.init();
    }

    init() {
        // Create chatbot HTML structure
        this.createChatbotHTML();

        // Add event listeners
        this.addEventListeners();

        // Add welcome message
        this.addBotMessage("Hello! I'm your IIITDMJ Student Attendance System assistant. How can I help you today?");
    }

    createChatbotHTML() {
        const chatbotHTML = `
            <div class="chatbot-toggle">
                <i class="fas fa-comments"></i>
            </div>
            <div class="chatbot-container chatbot-minimized">
                <div class="chatbot-header">
                    <h3>IIITDMJ Assistant</h3>
                    <div>
                        <i class="fas fa-minus chatbot-minimize"></i>
                    </div>
                </div>
                <div class="chatbot-body">
                    <div class="chatbot-messages"></div>
                </div>
                <div class="chatbot-input">
                    <input type="text" placeholder="Type your question here...">
                    <button><i class="fas fa-paper-plane"></i></button>
                </div>
            </div>
        `;

        // Append to body
        document.body.insertAdjacentHTML('beforeend', chatbotHTML);

        // Store references to elements
        this.chatbotToggle = document.querySelector('.chatbot-toggle');
        this.chatbotContainer = document.querySelector('.chatbot-container');
        this.chatbotHeader = document.querySelector('.chatbot-header');
        this.chatbotMinimize = document.querySelector('.chatbot-minimize');
        this.chatbotMessages = document.querySelector('.chatbot-messages');
        this.chatbotInput = document.querySelector('.chatbot-input input');
        this.chatbotSendButton = document.querySelector('.chatbot-input button');
    }

    addEventListeners() {
        // Toggle chatbot
        this.chatbotToggle.addEventListener('click', () => this.toggleChatbot());
        this.chatbotMinimize.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleChatbot();
        });

        // Send message on button click
        this.chatbotSendButton.addEventListener('click', () => this.sendMessage());

        // Send message on Enter key
        this.chatbotInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }

    toggleChatbot() {
        this.isOpen = !this.isOpen;

        if (this.isOpen) {
            this.chatbotContainer.classList.remove('chatbot-minimized');
            this.chatbotToggle.style.display = 'none';
            this.chatbotInput.focus();
        } else {
            this.chatbotContainer.classList.add('chatbot-minimized');
            this.chatbotToggle.style.display = 'flex';
        }
    }

    sendMessage() {
        const message = this.chatbotInput.value.trim();

        if (message) {
            // Add user message to chat
            this.addUserMessage(message);

            // Clear input
            this.chatbotInput.value = '';

            // Show typing indicator
            this.showTypingIndicator();

            // Store current question
            this.currentQuestion = message;

            // Send to backend
            this.sendToBackend(message);
        }
    }

    addUserMessage(message) {
        const messageHTML = `
            <div class="message user-message">
                ${message}
            </div>
        `;

        this.chatbotMessages.insertAdjacentHTML('beforeend', messageHTML);
        this.scrollToBottom();
    }

    addBotMessage(message, faqId = null) {
        // Remove typing indicator if present
        this.removeTypingIndicator();

        const messageHTML = `
            <div class="message bot-message">
                ${message}
            </div>
            ${faqId ? `
            <div class="chatbot-feedback">
                Was this helpful?
                <button class="feedback-yes" data-faq-id="${faqId}"><i class="fas fa-thumbs-up"></i></button>
                <button class="feedback-no" data-faq-id="${faqId}"><i class="fas fa-thumbs-down"></i></button>
            </div>
            ` : ''}
        `;

        this.chatbotMessages.insertAdjacentHTML('beforeend', messageHTML);
        this.scrollToBottom();

        // Add event listeners for feedback buttons
        if (faqId) {
            this.currentFaqId = faqId;
            const yesButton = this.chatbotMessages.querySelector(`.feedback-yes[data-faq-id="${faqId}"]`);
            const noButton = this.chatbotMessages.querySelector(`.feedback-no[data-faq-id="${faqId}"]`);

            yesButton.addEventListener('click', () => this.sendFeedback(true));
            noButton.addEventListener('click', () => this.sendFeedback(false));
        }
    }

    showTypingIndicator() {
        const typingHTML = `
            <div class="chatbot-typing">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;

        this.chatbotMessages.insertAdjacentHTML('beforeend', typingHTML);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const typingIndicator = this.chatbotMessages.querySelector('.chatbot-typing');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        this.chatbotMessages.scrollTop = this.chatbotMessages.scrollHeight;
    }

    sendToBackend(message) {
        // Simulate network delay
        setTimeout(() => {
            fetch('/chatbot/query/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: message }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    this.addBotMessage(data.answer, data.faq_id);
                } else if (data.status === 'ai_response') {
                    // Handle AI-generated response (no feedback buttons)
                    this.addBotMessage(data.answer);
                } else {
                    this.addBotMessage(data.answer || "Sorry, I couldn't process your request.");
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.addBotMessage("Sorry, there was an error processing your request. Please try again later.");
            });
        }, 1000);
    }

    sendFeedback(helpful) {
        fetch('/chatbot/feedback/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                faq_id: this.currentFaqId,
                question: this.currentQuestion,
                helpful: helpful
            }),
        })
        .then(response => response.json())
        .then(data => {
            // Remove feedback buttons
            const feedbackDiv = this.chatbotMessages.querySelector(`.chatbot-feedback`);
            if (feedbackDiv) {
                feedbackDiv.innerHTML = helpful ?
                    '<i class="fas fa-check"></i> Thanks for your feedback!' :
                    '<i class="fas fa-check"></i> Thanks for your feedback!';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Load CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.type = 'text/css';
    link.href = '/static/css/chatbot.css';
    document.head.appendChild(link);

    // Initialize chatbot
    const chatbot = new Chatbot();
});