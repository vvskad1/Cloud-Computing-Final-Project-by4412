// Ticket Tracking JavaScript
// This file handles ticket search and display functionality

// Tab switching
function showTab(tabName) {
    const idSection = document.getElementById('searchIdSection');
    const emailSection = document.getElementById('searchEmailSection');
    const idTab = document.getElementById('searchByIdTab');
    const emailTab = document.getElementById('searchByEmailTab');
    
    if (tabName === 'id') {
        idSection.classList.remove('hidden');
        emailSection.classList.add('hidden');
        idTab.classList.remove('btn-outline');
        idTab.classList.add('btn-primary');
        emailTab.classList.remove('btn-primary');
        emailTab.classList.add('btn-outline');
    } else {
        idSection.classList.add('hidden');
        emailSection.classList.remove('hidden');
        emailTab.classList.remove('btn-outline');
        emailTab.classList.add('btn-primary');
        idTab.classList.remove('btn-primary');
        idTab.classList.add('btn-outline');
    }
    
    // Hide results and errors
    document.getElementById('resultsSection').classList.add('hidden');
    document.getElementById('searchError').classList.add('hidden');
}

// Search by Ticket ID with API integration
async function searchByTicketId() {
    const ticketId = document.getElementById('ticketId').value;
    
    if (!ticketId) {
        showSearchError('Please enter a ticket ID');
        return;
    }
    
    hideSearchError();
    
    try {
        const response = await fetch(`/api/v1/tickets/${ticketId}`);
        
        if (response.ok) {
            const ticket = await response.json();
            await loadTicketHistory(ticketId);
            displayTicketDetail(ticket);
        } else {
            const error = await response.json();
            showSearchError(error.detail || `Ticket #${ticketId} not found`);
        }
    } catch (error) {
        console.error('Error fetching ticket:', error);
        showSearchError('Network error. Please try again.');
    }
}

// Search by Email with API integration
async function searchByEmail() {
    const email = document.getElementById('customerEmailSearch').value;
    
    if (!email) {
        showSearchError('Please enter an email address');
        return;
    }
    
    hideSearchError();
    
    try {
        const response = await fetch(`/api/v1/tickets/customer/${encodeURIComponent(email)}`);
        
        if (response.ok) {
            const tickets = await response.json();
            
            if (tickets.length === 0) {
                showSearchError('No tickets found for this email address');
            } else {
                displayTicketsList(tickets);
            }
        } else {
            const error = await response.json();
            showSearchError(error.detail || 'Error fetching tickets');
        }
    } catch (error) {
        console.error('Error fetching tickets:', error);
        showSearchError('Network error. Please try again.');
    }
}

// Load ticket history from API
async function loadTicketHistory(ticketId) {
    try {
        const response = await fetch(`/api/v1/tickets/${ticketId}/history`);
        
        if (response.ok) {
            const history = await response.json();
            displayTicketHistory(history);
        } else {
            console.error('Failed to load ticket history');
        }
    } catch (error) {
        console.error('Error loading ticket history:', error);
    }
}

// Display ticket history
function displayTicketHistory(history) {
    const historyContainer = document.getElementById('ticketHistory');
    
    if (history.length === 0) {
        historyContainer.innerHTML = '<p style="color: var(--text-secondary); text-align: center;">No status changes recorded yet</p>';
        return;
    }
    
    historyContainer.innerHTML = history.map(entry => `
        <div style="padding: 0.75rem; border-left: 3px solid var(--primary-color); margin-bottom: 0.75rem; background-color: var(--bg-white); border-radius: var(--radius-sm);">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                <strong>${entry.old_status ? entry.old_status : 'Created'} → ${entry.new_status}</strong>
                <span style="font-size: 0.875rem; color: var(--text-secondary);">${formatDate(entry.changed_at)}</span>
            </div>
            ${entry.changed_by ? `<p style="font-size: 0.875rem; color: var(--text-secondary);">Changed by: ${entry.changed_by}</p>` : ''}
            ${entry.notes ? `<p style="font-size: 0.875rem; margin-top: 0.5rem;">${entry.notes}</p>` : ''}
        </div>
    `).join('');
}

// Show search error
function showSearchError(message) {
    const errorDiv = document.getElementById('searchError');
    document.getElementById('searchErrorText').textContent = message;
    errorDiv.classList.remove('hidden');
}

// Hide search error
function hideSearchError() {
    document.getElementById('searchError').classList.add('hidden');
}

// Display single ticket detail
function displayTicketDetail(ticket) {
    const detailDiv = document.getElementById('ticketDetail');
    
    // Populate ticket details
    document.getElementById('detailTicketId').textContent = ticket.ticket_id;
    document.getElementById('detailStatus').textContent = ticket.status;
    document.getElementById('detailStatus').className = `badge badge-${ticket.status.replace('_', '-')}`;
    
    document.getElementById('detailCustomerName').textContent = ticket.customer.name;
    document.getElementById('detailCustomerEmail').textContent = ticket.customer.email;
    document.getElementById('detailCustomerPhone').textContent = ticket.customer.phone;
    
    document.getElementById('detailDeviceType').textContent = ticket.device.device_type;
    document.getElementById('detailDeviceBrand').textContent = ticket.device.brand;
    document.getElementById('detailDeviceModel').textContent = ticket.device.model;
    document.getElementById('detailIssue').textContent = ticket.device.issue_description;
    
    document.getElementById('detailPriority').textContent = ticket.priority;
    document.getElementById('detailPriority').className = `badge badge-${ticket.priority}`;
    
    document.getElementById('detailCreated').textContent = formatDate(ticket.created_at);
    document.getElementById('detailUpdated').textContent = formatDate(ticket.updated_at);
    document.getElementById('detailEstimatedCost').textContent = ticket.estimated_cost || 'TBD';
    document.getElementById('detailActualCost').textContent = ticket.actual_cost || 'TBD';
    
    if (ticket.completed_at) {
        document.getElementById('detailCompletedRow').classList.remove('hidden');
        document.getElementById('detailCompleted').textContent = formatDate(ticket.completed_at);
    } else {
        document.getElementById('detailCompletedRow').classList.add('hidden');
    }
    
    // Show detail section
    document.getElementById('ticketsList').classList.add('hidden');
    detailDiv.classList.remove('hidden');
    document.getElementById('resultsSection').classList.remove('hidden');
    hideSearchError();
}

// Display multiple tickets
function displayTicketsList(tickets) {
    const listDiv = document.getElementById('ticketsList');
    const container = document.getElementById('ticketsContainer');
    
    document.getElementById('ticketsCount').textContent = tickets.length;
    
    container.innerHTML = tickets.map(ticket => `
        <div class="card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin-bottom: 0.5rem;">Ticket #${ticket.ticket_id}</h3>
                    <p style="color: var(--text-secondary);">${ticket.device.brand} ${ticket.device.model}</p>
                </div>
                <span class="badge badge-${ticket.status.replace('_', '-')}">${ticket.status}</span>
            </div>
            <p style="margin-top: 1rem; font-size: 0.875rem; color: var(--text-secondary);">
                Created: ${formatDate(ticket.created_at)}
            </p>
        </div>
    `).join('');
    
    document.getElementById('ticketDetail').classList.add('hidden');
    listDiv.classList.remove('hidden');
    document.getElementById('resultsSection').classList.remove('hidden');
    hideSearchError();
}

// Format date helper
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Status badge helper
function getStatusBadgeClass(status) {
    return `badge badge-${status.replace('_', '-')}`;
}
