// Customer Portal JavaScript

// Check authentication on page load
document.addEventListener('DOMContentLoaded', function() {
    checkAuthentication();
    loadCustomerData();
    loadTickets();
    loadNotifications();
});

// Check if customer is authenticated
function checkAuthentication() {
    const token = localStorage.getItem('customer_token');
    if (!token) {
        window.location.href = '/static/login.html';
        return;
    }
    
    // Display customer info
    const customerName = localStorage.getItem('customer_name');
    if (customerName) {
        document.getElementById('welcomeMessage').textContent = `Welcome, ${customerName}!`;
        displayCustomerInfo(customerName);
    }
}

// Display customer information in navbar
function displayCustomerInfo(customerName) {
    const customerInfo = document.getElementById('customerInfo');
    customerInfo.innerHTML = `
        <div style="display: flex; align-items: center; gap: 1rem;">
            <span style="color: white; font-weight: 500;">👤 ${customerName}</span>
            <button onclick="logout()" class="btn btn-outline" style="padding: 0.5rem 1rem;">Logout</button>
        </div>
    `;
}

// Logout function
function logout() {
    localStorage.removeItem('customer_token');
    localStorage.removeItem('customer_id');
    localStorage.removeItem('customer_name');
    localStorage.removeItem('customer_email');
    window.location.href = '/static/login.html';
}

// Get authorization headers
function getAuthHeaders() {
    const token = localStorage.getItem('customer_token');
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
}

// Handle authentication errors
function handleAuthError(response) {
    if (response.status === 401) {
        alert('Session expired. Please login again.');
        logout();
        return true;
    }
    return false;
}

// Load customer profile data
async function loadCustomerData() {
    try {
        const response = await fetch('/api/v1/customer/profile', {
            headers: getAuthHeaders()
        });
        
        if (handleAuthError(response)) return;
        
        if (response.ok) {
            const profile = await response.json();
            
            // Update notification badge
            if (profile.unread_notifications > 0) {
                const badge = document.getElementById('notificationBadge');
                badge.textContent = profile.unread_notifications;
                badge.classList.remove('hidden');
            }
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

// Load customer tickets
async function loadTickets() {
    try {
        const response = await fetch('/api/v1/customer/tickets', {
            headers: getAuthHeaders()
        });
        
        if (handleAuthError(response)) return;
        
        if (response.ok) {
            const tickets = await response.json();
            displayTickets(tickets);
            updateTicketStats(tickets);
        } else {
            document.getElementById('ticketsContainer').innerHTML = 
                '<p style="text-align: center; color: var(--danger-color); padding: 2rem;">Failed to load tickets</p>';
        }
    } catch (error) {
        console.error('Error loading tickets:', error);
        document.getElementById('ticketsContainer').innerHTML = 
            '<p style="text-align: center; color: var(--danger-color); padding: 2rem;">Network error loading tickets</p>';
    }
}

// Display tickets
function displayTickets(tickets) {
    const container = document.getElementById('ticketsContainer');
    
    if (tickets.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 3rem;">
                <p style="color: var(--text-secondary); margin-bottom: 1rem;">No repair tickets yet</p>
                <a href="/static/new-booking.html" class="btn btn-primary">Book Your First Repair</a>
            </div>
        `;
        return;
    }
    
    container.innerHTML = tickets.map(ticket => `
        <div class="card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                <div>
                    <h3 style="margin-bottom: 0.5rem;">Ticket #${ticket.ticket_id}</h3>
                    <p style="color: var(--text-secondary); font-size: 0.875rem;">
                        ${ticket.device.brand} ${ticket.device.model} (${ticket.device.device_type})
                    </p>
                </div>
                <span class="status-badge status-${ticket.status}">${ticket.status}</span>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1rem;">
                <div>
                    <strong>Priority:</strong> 
                    <span class="priority-badge priority-${ticket.priority}">${ticket.priority}</span>
                </div>
                <div><strong>Cost:</strong> ${ticket.estimated_cost ? '$' + ticket.estimated_cost.toFixed(2) : 'TBD'}</div>
                <div><strong>Created:</strong> ${formatDate(ticket.created_at)}</div>
                <div><strong>Updated:</strong> ${formatDate(ticket.updated_at)}</div>
            </div>
            
            <div style="padding: 0.75rem; background-color: var(--bg-light); border-radius: var(--radius-sm);">
                <strong>Issue:</strong> ${ticket.device.issue_description}
            </div>
        </div>
    `).join('');
}

// Update ticket statistics
function updateTicketStats(tickets) {
    const total = tickets.length;
    const active = tickets.filter(t => !['completed', 'delivered', 'cancelled'].includes(t.status)).length;
    const completed = tickets.filter(t => ['completed', 'delivered'].includes(t.status)).length;
    
    document.getElementById('totalTicketsCount').textContent = total;
    document.getElementById('activeTicketsCount').textContent = active;
    document.getElementById('completedTicketsCount').textContent = completed;
}

// Load notifications
async function loadNotifications() {
    try {
        const response = await fetch('/api/v1/customer/notifications', {
            headers: getAuthHeaders()
        });
        
        if (handleAuthError(response)) return;
        
        if (response.ok) {
            const notifications = await response.json();
            displayNotifications(notifications);
        } else {
            document.getElementById('notificationsContainer').innerHTML = 
                '<p style="text-align: center; color: var(--danger-color); padding: 2rem;">Failed to load notifications</p>';
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
        document.getElementById('notificationsContainer').innerHTML = 
            '<p style="text-align: center; color: var(--danger-color); padding: 2rem;">Network error loading notifications</p>';
    }
}

// Display notifications
function displayNotifications(notifications) {
    const container = document.getElementById('notificationsContainer');
    
    if (notifications.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 2rem;">No notifications</p>';
        return;
    }
    
    container.innerHTML = notifications.map(notification => `
        <div class="notification-item ${notification.is_read ? 'read' : 'unread'}" 
             onclick="markAsRead(${notification.notification_id})">
            <div style="display: flex; justify-content: between; align-items: flex-start;">
                <div style="flex: 1;">
                    <p style="margin-bottom: 0.5rem;">${notification.message}</p>
                    <p style="font-size: 0.875rem; color: var(--text-secondary);">
                        ${formatDate(notification.created_at)}
                        ${!notification.is_read ? '<strong style="color: var(--primary-color);"> • Unread</strong>' : ''}
                    </p>
                </div>
            </div>
        </div>
    `).join('');
}

// Mark notification as read
async function markAsRead(notificationId) {
    try {
        const response = await fetch(`/api/v1/customer/notifications/${notificationId}/read`, {
            method: 'PATCH',
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            // Reload notifications and profile
            loadNotifications();
            loadCustomerData();
        }
    } catch (error) {
        console.error('Error marking notification as read:', error);
    }
}

// Section switching
function showSection(section) {
    const ticketsSection = document.getElementById('ticketsSection');
    const notificationsSection = document.getElementById('notificationsSection');
    const ticketsTab = document.getElementById('ticketsTab');
    const notificationsTab = document.getElementById('notificationsTab');
    
    if (section === 'tickets') {
        ticketsSection.classList.remove('hidden');
        notificationsSection.classList.add('hidden');
        ticketsTab.classList.remove('btn-outline');
        ticketsTab.classList.add('btn-primary');
        notificationsTab.classList.remove('btn-primary');
        notificationsTab.classList.add('btn-outline');
    } else {
        ticketsSection.classList.add('hidden');
        notificationsSection.classList.remove('hidden');
        notificationsTab.classList.remove('btn-outline');
        notificationsTab.classList.add('btn-primary');
        ticketsTab.classList.remove('btn-primary');
        ticketsTab.classList.add('btn-outline');
    }
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Auto-refresh every 30 seconds
setInterval(function() {
    loadCustomerData();
    loadNotifications();
}, 30000);


// ============================================================================
// AI Chatbot Functions
// ============================================================================

let conversationHistory = [];

function toggleChatbot() {
    const chatWindow = document.getElementById('chatbotWindow');
    
    if (chatWindow.style.display === 'none' || chatWindow.style.display === '') {
        chatWindow.style.display = 'flex';
        document.getElementById('chatInput').focus();
    } else {
        chatWindow.style.display = 'none';
    }
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to UI
    addMessageToChat('user', message);
    input.value = '';
    
    // Add user message to history
    conversationHistory.push({
        role: 'user',
        content: message
    });
    
    // Show typing indicator
    const typingId = addTypingIndicator();
    
    try {
        const response = await fetch('/api/v1/chatbot', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                message: message,
                conversation_history: conversationHistory
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to get response');
        }
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        // Add bot response to UI
        addMessageToChat('bot', data.response);
        
        // Add bot response to history
        conversationHistory.push({
            role: 'assistant',
            content: data.response
        });
        
        // Keep only last 10 messages in history
        if (conversationHistory.length > 10) {
            conversationHistory = conversationHistory.slice(-10);
        }
        
    } catch (error) {
        console.error('Chatbot error:', error);
        removeTypingIndicator(typingId);
        addMessageToChat('bot', '❌ Sorry, I encountered an error. Please try again.');
    }
}

function addMessageToChat(sender, text) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;
    messageDiv.style.marginBottom = '1rem';
    messageDiv.style.display = 'flex';
    messageDiv.style.justifyContent = sender === 'user' ? 'flex-end' : 'flex-start';
    
    const bubbleStyle = sender === 'user' 
        ? 'background: linear-gradient(135deg, #667eea, #764ba2); color: white;' 
        : 'background: white; color: #333;';
    
    messageDiv.innerHTML = `
        <div style="
            ${bubbleStyle}
            padding: 0.75rem;
            border-radius: 10px;
            max-width: 80%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        ">
            <p style="margin: 0; font-size: 0.9rem; line-height: 1.4;">${escapeHtml(text)}</p>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    const typingId = 'typing-' + Date.now();
    typingDiv.id = typingId;
    typingDiv.style.marginBottom = '1rem';
    
    typingDiv.innerHTML = `
        <div style="
            background: white;
            padding: 0.75rem;
            border-radius: 10px;
            max-width: 80%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        ">
            <p style="margin: 0; font-size: 0.9rem; color: #999;">
                <span style="animation: blink 1.4s infinite;">●</span>
                <span style="animation: blink 1.4s infinite 0.2s;">●</span>
                <span style="animation: blink 1.4s infinite 0.4s;">●</span>
            </p>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return typingId;
}

function removeTypingIndicator(typingId) {
    const typingDiv = document.getElementById(typingId);
    if (typingDiv) {
        typingDiv.remove();
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
