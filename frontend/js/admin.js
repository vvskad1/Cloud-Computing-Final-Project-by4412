// Admin Dashboard JavaScript
// This file handles admin functionality for managing tickets and viewing statistics

let currentTicketId = null;

// Check authentication on page load
document.addEventListener('DOMContentLoaded', function() {
    checkAuthentication();
    loadDashboardStats();
    loadTickets();
});

// Check if user is authenticated
function checkAuthentication() {
    const token = localStorage.getItem('admin_token');
    if (!token) {
        window.location.href = '/static/login.html';
        return;
    }
    
    // Display admin info
    const adminName = localStorage.getItem('admin_full_name');
    if (adminName) {
        displayAdminInfo(adminName);
    }
}

// Display admin information in the UI
function displayAdminInfo(adminName) {
    const navbar = document.getElementById('adminNavbar');
    if (navbar) {
        navbar.innerHTML = `
            <span style="color: white; font-weight: 500;">👤 ${adminName}</span>
            <button onclick="logout()" class="btn btn-outline" style="padding: 0.5rem 1rem;">Logout</button>
        `;
    }
}

// Logout function
function logout() {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_username');
    localStorage.removeItem('admin_full_name');
    window.location.href = '/static/login.html';
}

// Helper function to get authorization headers
function getAuthHeaders() {
    const token = localStorage.getItem('admin_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

// Helper function to handle authentication errors
function handleAuthError(response) {
    if (response.status === 401) {
        alert('Session expired. Please login again.');
        logout();
        return true;
    }
    return false;
}

// Load dashboard statistics with API integration
async function loadDashboardStats() {
    try {
        const response = await fetch('/api/v1/admin/dashboard', {
            headers: getAuthHeaders()
        });
        
        if (handleAuthError(response)) return;
        
        if (response.ok) {
            const stats = await response.json();
            
            const statsHTML = `
                <div class="stat-card" style="border-left-color: var(--primary-color);">
                    <div class="stat-label">Total Tickets</div>
                    <div class="stat-value">${stats.total_tickets}</div>
                </div>
                <div class="stat-card" style="border-left-color: var(--secondary-color);">
                    <div class="stat-label">Total Customers</div>
                    <div class="stat-value">${stats.total_customers}</div>
                </div>
                <div class="stat-card" style="border-left-color: var(--warning-color);">
                    <div class="stat-label">Avg. Cost</div>
                    <div class="stat-value">$${stats.average_estimated_cost.toFixed(2)}</div>
                </div>
                <div class="stat-card" style="border-left-color: var(--danger-color);">
                    <div class="stat-label">High Priority</div>
                    <div class="stat-value">${stats.tickets_by_priority.high || 0}</div>
                </div>
                <div class="stat-card" style="border-left-color: var(--primary-light);">
                    <div class="stat-label">Medium Priority</div>
                    <div class="stat-value">${stats.tickets_by_priority.medium || 0}</div>
                </div>
                <div class="stat-card" style="border-left-color: var(--secondary-dark);">
                    <div class="stat-label">Low Priority</div>
                    <div class="stat-value">${stats.tickets_by_priority.low || 0}</div>
                </div>
            `;
            
            document.getElementById('statsGrid').innerHTML = statsHTML;
        } else {
            console.error('Failed to load dashboard statistics');
        }
    } catch (error) {
        console.error('Error loading dashboard statistics:', error);
    }
}

// Load all tickets with API integration
async function loadTickets() {
    const status = document.getElementById('filterStatus').value;
    const priority = document.getElementById('filterPriority').value;
    const customer = document.getElementById('filterCustomer').value;
    
    // Build query parameters
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (priority) params.append('priority', priority);
    if (customer) params.append('customer_name', customer);
    
    try {
        const url = `/api/v1/tickets${params.toString() ? '?' + params.toString() : ''}`;
        const response = await fetch(url, {
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const tickets = await response.json();
            displayTicketsTable(tickets);
        } else {
            console.error('Failed to load tickets');
            const tbody = document.getElementById('ticketsTableBody');
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" style="text-align: center; padding: 2rem; color: var(--danger-color);">
                        Failed to load tickets
                    </td>
                </tr>
            `;
        }
    } catch (error) {
        console.error('Error loading tickets:', error);
        const tbody = document.getElementById('ticketsTableBody');
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 2rem; color: var(--danger-color);">
                    Network error. Please try again.
                </td>
            </tr>
        `;
    }
}

// Apply filters
function applyFilters() {
    loadTickets();
}

// Clear filters
function clearFilters() {
    document.getElementById('filterStatus').value = '';
    document.getElementById('filterPriority').value = '';
    document.getElementById('filterCustomer').value = '';
    loadTickets();
}

// View ticket details with API integration
async function viewTicketDetail(ticketId) {
    currentTicketId = ticketId;
    
    const detailContent = document.getElementById('ticketDetailContent');
    detailContent.innerHTML = '<p style="text-align: center; padding: 2rem;">Loading...</p>';
    
    document.getElementById('ticketDetailModal').classList.remove('hidden');
    document.getElementById('ticketDetailModal').scrollIntoView({ behavior: 'smooth' });
    
    try {
        const response = await fetch(`/api/v1/tickets/${ticketId}`, {
            headers: getAuthHeaders()
        });
        
        if (handleAuthError(response)) return;
        
        if (response.ok) {
            const ticket = await response.json();
            
            // Populate update form
            document.getElementById('updateStatus').value = ticket.status;
            document.getElementById('updatePriority').value = ticket.priority;
            document.getElementById('updateNotes').value = '';
            
            // Display ticket details
            detailContent.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                    <div>
                        <strong>Ticket ID:</strong> #${ticket.ticket_id}
                    </div>
                    <div>
                        <strong>Status:</strong> <span class="badge badge-${ticket.status.replace('_', '-')}">${ticket.status}</span>
                    </div>
                    <div>
                        <strong>Priority:</strong> <span class="badge badge-${ticket.priority}">${ticket.priority}</span>
                    </div>
                    <div>
                        <strong>Created:</strong> ${formatDate(ticket.created_at)}
                    </div>
                    <div>
                        <strong>Updated:</strong> ${formatDate(ticket.updated_at)}
                    </div>
                    <div>
                        <strong>Estimated Cost:</strong> $${ticket.estimated_cost.toFixed(2)}
                    </div>
                </div>
                
                <hr style="margin: 1.5rem 0;">
                
                <h4>Customer Information</h4>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 1rem;">
                    <div><strong>Name:</strong> ${ticket.customer.name}</div>
                    <div><strong>Email:</strong> ${ticket.customer.email}</div>
                    <div><strong>Phone:</strong> ${ticket.customer.phone}</div>
                </div>
                
                <hr style="margin: 1.5rem 0;">
                
                <h4>Device Information</h4>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 1rem;">
                    <div><strong>Type:</strong> ${ticket.device.device_type}</div>
                    <div><strong>Brand:</strong> ${ticket.device.brand}</div>
                    <div><strong>Model:</strong> ${ticket.device.model}</div>
                    <div><strong>Serial:</strong> ${ticket.device.serial_number || 'N/A'}</div>
                </div>
                <div style="margin-top: 1rem;">
                    <strong>Issue Description:</strong>
                    <p style="margin-top: 0.5rem; padding: 0.75rem; background-color: var(--bg-light); border-radius: var(--radius-sm);">
                        ${ticket.device.issue_description}
                    </p>
                </div>
                
                ${ticket.notes ? `
                <hr style="margin: 1.5rem 0;">
                <h4>Notes</h4>
                <p style="padding: 0.75rem; background-color: var(--bg-light); border-radius: var(--radius-sm);">
                    ${ticket.notes}
                </p>
                ` : ''}
            `;
            
            // Load ticket history
            loadTicketHistory(ticketId);
        } else {
            detailContent.innerHTML = '<p style="text-align: center; padding: 2rem; color: var(--danger-color);">Failed to load ticket details</p>';
        }
    } catch (error) {
        console.error('Error loading ticket:', error);
        detailContent.innerHTML = '<p style="text-align: center; padding: 2rem; color: var(--danger-color);">Network error. Please try again.</p>';
    }
}

// Load ticket history
async function loadTicketHistory(ticketId) {
    try {
        const response = await fetch(`/api/v1/tickets/${ticketId}/history`, {
            headers: getAuthHeaders()
        });
        
        if (handleAuthError(response)) return;
        
        if (response.ok) {
            const history = await response.json();
            
            const historySection = document.createElement('div');
            historySection.innerHTML = `
                <hr style="margin: 1.5rem 0;">
                <h4>Status History</h4>
                <div style="margin-top: 1rem;">
                    ${history.length === 0 ? '<p style="color: var(--text-secondary);">No status changes yet</p>' : history.map(entry => `
                        <div style="padding: 0.75rem; border-left: 3px solid var(--primary-color); margin-bottom: 0.75rem; background-color: var(--bg-light); border-radius: var(--radius-sm);">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                                <strong>${entry.old_status || 'Created'} → ${entry.new_status}</strong>
                                <span style="font-size: 0.875rem; color: var(--text-secondary);">${formatDate(entry.changed_at)}</span>
                            </div>
                            ${entry.changed_by ? `<p style="font-size: 0.875rem; color: var(--text-secondary);">Changed by: ${entry.changed_by}</p>` : ''}
                            ${entry.notes ? `<p style="font-size: 0.875rem; margin-top: 0.5rem;">${entry.notes}</p>` : ''}
                        </div>
                    `).join('')}
                </div>
            `;
            
            document.getElementById('ticketDetailContent').appendChild(historySection);
        }
    } catch (error) {
        console.error('Error loading ticket history:', error);
    }
}

// Close ticket detail
function closeTicketDetail() {
    document.getElementById('ticketDetailModal').classList.add('hidden');
    currentTicketId = null;
}

// Update ticket with API integration
async function updateTicket() {
    if (!currentTicketId) {
        alert('No ticket selected');
        return;
    }
    
    const status = document.getElementById('updateStatus').value;
    const priority = document.getElementById('updatePriority').value;
    const notes = document.getElementById('updateNotes').value;
    
    const updateData = {};
    if (status) updateData.status = status;
    if (priority) updateData.priority = priority;
    if (notes) updateData.notes = notes;
    
    try {
        const response = await fetch(`/api/v1/tickets/${currentTicketId}`, {
            method: 'PATCH',
            headers: getAuthHeaders(),
            body: JSON.stringify(updateData)
        });
        
        if (handleAuthError(response)) return;
        
        if (response.ok) {
            alert('Ticket updated successfully!');
            closeTicketDetail();
            loadTickets(); // Refresh the tickets list
            loadDashboardStats(); // Refresh stats
        } else {
            const error = await response.json();
            alert(`Failed to update ticket: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error updating ticket:', error);
        alert('Network error. Please try again.');
    }
}

// Search customers with API integration
async function searchCustomers() {
    const searchTerm = document.getElementById('customerSearch').value;
    
    try {
        const url = `/api/v1/admin/customers${searchTerm ? '?search=' + encodeURIComponent(searchTerm) : ''}`;
        const response = await fetch(url, {
            headers: getAuthHeaders()
        });
        
        if (handleAuthError(response)) return;
        
        if (response.ok) {
            const customers = await response.json();
            displayCustomers(customers);
        } else {
            const container = document.getElementById('customersContainer');
            container.innerHTML = `
                <div style="margin-top: 1rem; padding: 1rem; background-color: var(--danger-light); color: var(--danger-color); border-radius: var(--radius-sm);">
                    Failed to load customers
                </div>
            `;
        }
    } catch (error) {
        console.error('Error searching customers:', error);
        const container = document.getElementById('customersContainer');
        container.innerHTML = `
            <div style="margin-top: 1rem; padding: 1rem; background-color: var(--danger-light); color: var(--danger-color); border-radius: var(--radius-sm);">
                Network error. Please try again.
            </div>
        `;
    }
}

// Display tickets in table
function displayTicketsTable(tickets) {
    const tbody = document.getElementById('ticketsTableBody');
    
    if (tickets.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 2rem;">
                    No tickets found
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = tickets.map(ticket => `
        <tr>
            <td>${ticket.ticket_id}</td>
            <td>${ticket.customer.name}</td>
            <td>${ticket.device.brand} ${ticket.device.model}</td>
            <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                ${ticket.device.issue_description}
            </td>
            <td>
                <span class="badge badge-${ticket.status.replace('_', '-')}">${ticket.status}</span>
            </td>
            <td>
                <span class="badge badge-${ticket.priority}">${ticket.priority}</span>
            </td>
            <td style="font-size: 0.875rem;">${formatDate(ticket.created_at)}</td>
            <td>
                <button onclick="viewTicketDetail(${ticket.ticket_id})" class="btn btn-primary" style="padding: 0.25rem 0.75rem; font-size: 0.875rem;">
                    View
                </button>
            </td>
        </tr>
    `).join('');
    
    document.getElementById('ticketCount').textContent = tickets.length;
}

// Format date helper
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

// Display customers
function displayCustomers(customers) {
    const container = document.getElementById('customersContainer');
    
    if (customers.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 1rem;">No customers found</p>';
        return;
    }
    
    container.innerHTML = `
        <table class="table" style="margin-top: 1rem;">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Registered</th>
                </tr>
            </thead>
            <tbody>
                ${customers.map(customer => `
                    <tr>
                        <td>${customer.customer_id}</td>
                        <td>${customer.name}</td>
                        <td>${customer.email}</td>
                        <td>${customer.phone}</td>
                        <td>${formatDate(customer.created_at)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}
