document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chatContainer');
    const symptomForm = document.getElementById('symptomForm');
    const followUpForm = document.getElementById('followUpForm');
    let currentConsultationId = null;

    // Load profile and history immediately
    loadProfile();
    loadHistory();

    // Function to load user profile
    async function loadProfile() {
        try {
            const response = await fetch('/profile');
            const data = await response.json();
            
            if (data.success && data.profile) {
                document.getElementById('userName').textContent = data.profile.name;
            } else {
                document.getElementById('userName').textContent = 'User';
            }
        } catch (error) {
            console.error('Error loading profile:', error);
            document.getElementById('userName').textContent = 'User';
        }
    }

    // Function to load chat history
    async function loadHistory() {
        console.log('Loading history...');
        try {
            const response = await fetch('/history');
            const data = await response.json();
            console.log('History data:', data);
            
            if (data.success && data.history) {
                updateChatList(data.history);
            } else {
                console.log('No history data or success false');
                updateChatList([]);
            }
        } catch (error) {
            console.error('Error loading history:', error);
            updateChatList([]);
        }
    }

    // Function to update chat list
    function updateChatList(consultations) {
        const chatList = document.getElementById('chatList');
        
        if (!consultations || consultations.length === 0) {
            chatList.innerHTML = `
                <div class="text-center p-3">
                    <small class="text-muted">No previous chats</small>
                </div>
            `;
            return;
        }

        chatList.innerHTML = consultations.map(chat => `
            <div class="chat-item ${chat.id === currentConsultationId ? 'active' : ''}" 
                 onclick="loadChat(${chat.id})">
                <div class="chat-item-content">
                    <div class="chat-item-title">
                        ${formatDate(chat.created_at)}
                    </div>
                    <div class="chat-item-preview">
                        ${escapeHtml(formatPreview(chat))}
                    </div>
                </div>
                <div class="chat-item-actions">
                    <button onclick="event.stopPropagation(); deleteChat(${chat.id})" 
                            class="delete-btn" title="Delete chat">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    function formatPreview(chat) {
        const preview = `${chat.age} years, ${chat.gender} - ${chat.symptoms}`;
        return preview.length > 60 ? preview.substring(0, 57) + '...' : preview;
    }

    function formatDate(dateString) {
        try {
            const date = new Date(dateString);
            const now = new Date();
            const diff = now - date;
            const days = Math.floor(diff / (1000 * 60 * 60 * 24));

            if (days === 0) {
                return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            } else if (days === 1) {
                return 'Yesterday';
            } else if (days < 7) {
                return date.toLocaleDateString([], { weekday: 'long' });
            } else {
                return date.toLocaleDateString([], { 
                    month: 'short', 
                    day: 'numeric',
                    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
                });
            }
        } catch (e) {
            console.error('Date formatting error:', e);
            return dateString;
        }
    }

    // Make loadChat and deleteChat available globally
    window.loadChat = async function(chatId) {
        console.log('Loading chat:', chatId);
        try {
            const response = await fetch(`/consultation/${chatId}`);
            const data = await response.json();
            console.log('Chat data:', data);
            
            if (data.success) {
                currentConsultationId = chatId;
                chatContainer.innerHTML = '';
                
                // Add initial consultation
                addUserMessage(`Age: ${data.consultation.age}, Gender: ${data.consultation.gender}, Symptoms: ${data.consultation.symptoms}`);
                addAIMessage(data.consultation.initial_response);

                // Switch to follow-up form
                symptomForm.style.display = 'none';
                followUpForm.style.display = 'block';

                // Update active state in chat list
                document.querySelectorAll('.chat-item').forEach(item => {
                    item.classList.remove('active');
                });
                const activeItem = document.querySelector(`.chat-item[onclick*="loadChat(${chatId})"]`);
                if (activeItem) activeItem.classList.add('active');
            }
        } catch (error) {
            console.error('Error loading chat:', error);
        }
    };

    window.deleteChat = async function(chatId) {
        if (!confirm('Are you sure you want to delete this chat?')) return;

        try {
            const response = await fetch(`/consultation/${chatId}`, {
                method: 'DELETE'
            });
            const data = await response.json();
            
            if (data.success) {
                if (currentConsultationId === chatId) {
                    startNewConsultation();
                }
                loadHistory();
            }
        } catch (error) {
            console.error('Error deleting chat:', error);
        }
    };

    // Add welcome message
    addAIMessage("👋 Hello! I'm DR. AI. Please provide your age, gender, and describe your symptoms.");

    // Handle initial symptoms form
    symptomForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const age = parseInt(document.getElementById('age').value);
        const gender = document.getElementById('gender').value;
        const symptoms = document.getElementById('initialSymptoms').value;

        // Age validation
        if (age <= 0 || age > 150) {
            alert('Please enter a valid age between 1 and 150 years.');
            return;
        }

        if (!symptomForm.checkValidity()) {
            symptomForm.classList.add('was-validated');
            return;
        }

        addUserMessage(`Age: ${age}, Gender: ${gender}, Symptoms: ${symptoms}`);
        showTypingIndicator();

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ age, gender, symptoms })
            });

            const data = await response.json();
            hideTypingIndicator();

            if (data.success) {
                currentConsultationId = data.consultation_id;
                addAIMessage(data.response);
                loadHistory();
                
                // Clear symptoms
                document.getElementById('initialSymptoms').value = '';
                
                // Switch to follow-up form
                symptomForm.style.display = 'none';
                followUpForm.style.display = 'block';
            } else {
                addAIMessage("I apologize, but I'm having trouble analyzing your symptoms. Please try again.");
            }
        } catch (error) {
            console.error('Error:', error);
            hideTypingIndicator();
            addAIMessage("I'm sorry, but I'm having technical difficulties. Please try again.");
        }
    });

    // Handle follow-up form
    followUpForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const message = document.getElementById('followUpMessage').value;
        if (!message.trim()) return;

        addUserMessage(message);
        showTypingIndicator();
        document.getElementById('followUpMessage').value = '';

        try {
            const response = await fetch('/follow_up', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    consultation_id: currentConsultationId 
                })
            });

            const data = await response.json();
            hideTypingIndicator();

            if (data.success) {
                addAIMessage(data.response);
                loadHistory();
            } else {
                addAIMessage("I'm sorry, I couldn't process your message. Please try again.");
            }
        } catch (error) {
            console.error('Error:', error);
            hideTypingIndicator();
            addAIMessage("I'm sorry, I'm having trouble responding. Please try again.");
        }
    });

    // Function to start a new consultation
    window.startNewConsultation = function() {
        currentConsultationId = null;
        
        // Clear inputs
        document.getElementById('age').value = '';
        document.getElementById('gender').value = '';
        document.getElementById('initialSymptoms').value = '';
        document.getElementById('followUpMessage').value = '';
        
        // Reset forms
        symptomForm.style.display = 'block';
        followUpForm.style.display = 'none';
        
        // Clear chat
        chatContainer.innerHTML = '';
        
        // Add welcome message
        addAIMessage("👋 Hello! I'm DR. AI. Please provide your age, gender, and describe your symptoms.");
    };

    function addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `
            <div class="message-bubble">
                ${escapeHtml(message)}
            </div>
        `;
        chatContainer.appendChild(messageDiv);
        scrollToBottom();
    }

    function addAIMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ai-message';
        messageDiv.innerHTML = `
            <div class="message-bubble">
                <div class="message-header">
                    <i class="fas fa-robot"></i>
                    <strong>DR. AI</strong>
                </div>
                <div class="message-content">
                    ${formatAIMessage(message)}
                </div>
            </div>
        `;
        chatContainer.appendChild(messageDiv);
        scrollToBottom();
    }

    function formatAIMessage(message) {
        if (!message) return 'No response available';
        return message
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>')
            .replace(/\*/g, '')
            .replace(/(🏥.*?:)/g, '<strong class="section-header">$1</strong>')
            .replace(/(⚠️.*?:)/g, '<strong class="section-header">$1</strong>')
            .replace(/(💊.*?:)/g, '<strong class="section-header">$1</strong>')
            .replace(/(❓.*?:)/g, '<strong class="section-header">$1</strong>')
            .replace(/(⚕️.*?:)/g, '<strong class="section-header">$1</strong>');
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai-message typing-indicator';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="message-bubble">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        chatContainer.appendChild(typingDiv);
        scrollToBottom();
    }

    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});

// Add this to window scope for the report generation
window.generateReport = async function(consultationId) {
    try {
        const response = await fetch(`/generate_report/${consultationId}`);
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `medical_report_${consultationId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        } else {
            alert('Error generating report. Please try again.');
        }
    } catch (error) {
        console.error('Error generating report:', error);
        alert('Error generating report. Please try again.');
    }
};

function handleError(error) {
    console.error('DR. AI Error:', error);
    addAIMessage("I apologize, but I'm having trouble processing your request. Please try again or start a new consultation.");
} 