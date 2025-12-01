// Booking Form JavaScript
// This file handles form validation and submission for new repair bookings

document.addEventListener('DOMContentLoaded', function() {
    // Update navbar based on login status
    updateNavbar();
    
    // Auto-fill customer information if logged in
    autoFillCustomerInfo();
    
    const form = document.getElementById('bookingForm');
    const successMessage = document.getElementById('successMessage');
    const errorMessage = document.getElementById('errorMessage');

    // Form submission handler with API integration
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Hide previous messages
        successMessage.classList.add('hidden');
        errorMessage.classList.add('hidden');

        // Disable submit button
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';

        // Get form data
        const formData = {
            customer_name: document.getElementById('customerName').value,
            customer_email: document.getElementById('customerEmail').value,
            customer_phone: document.getElementById('customerPhone').value,
            device_type: document.getElementById('deviceType').value,
            device_brand: document.getElementById('deviceBrand').value,
            device_model: document.getElementById('deviceModel').value,
            serial_number: document.getElementById('serialNumber').value || null,
            issue_description: document.getElementById('issueDescription').value,
            priority: document.getElementById('priority').value,
            estimated_cost: parseFloat(document.getElementById('estimatedCost').value) || null,
            notes: document.getElementById('notes').value || null
        };

        try {
            // Submit to API
            const response = await fetch('/api/v1/tickets', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                // Show success message
                document.getElementById('ticketId').textContent = data.ticket_id;
                successMessage.classList.remove('hidden');
                
                // Scroll to top to show message
                window.scrollTo({ top: 0, behavior: 'smooth' });
                
                // Reset form
                form.reset();
            } else {
                // Show error message
                let errorMsg = 'Failed to create booking. ';
                if (data.detail) {
                    if (Array.isArray(data.detail)) {
                        errorMsg += data.detail.map(err => err.msg).join(', ');
                    } else {
                        errorMsg += data.detail;
                    }
                }
                showError(errorMsg);
            }
        } catch (error) {
            console.error('Error submitting booking:', error);
            showError('Network error. Please check your connection and try again.');
        } finally {
            // Re-enable submit button
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });

    // Real-time form validation
    const phoneInput = document.getElementById('customerPhone');
    phoneInput.addEventListener('input', function() {
        if (this.value.length > 0 && this.value.length < 10) {
            this.setCustomValidity('Phone number must be at least 10 characters');
        } else {
            this.setCustomValidity('');
        }
    });

    const issueDesc = document.getElementById('issueDescription');
    issueDesc.addEventListener('input', function() {
        if (this.value.length > 0 && this.value.length < 10) {
            this.setCustomValidity('Issue description must be at least 10 characters');
        } else {
            this.setCustomValidity('');
        }
    });
});

// Helper function to show error
function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    document.getElementById('errorText').textContent = message;
    errorMessage.classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Update navbar based on customer login status
function updateNavbar() {
    const customerToken = localStorage.getItem('customer_token');
    const customerName = localStorage.getItem('customer_name');
    const navLinks = document.getElementById('navLinks');
    const userInfo = document.getElementById('userInfo');
    
    if (customerToken && customerName) {
        // Customer is logged in - show customer navbar
        navLinks.innerHTML = `
            <a href="/static/customer-portal.html">My Portal</a>
            <a href="/static/new-booking.html" class="active">Book Repair</a>
        `;
        
        userInfo.innerHTML = `
            <span style="color: white; margin-right: 1rem;">👤 ${customerName}</span>
            <button onclick="logout()" style="background: rgba(255,255,255,0.2); color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">Logout</button>
        `;
    } else {
        // Not logged in - show public navbar
        navLinks.innerHTML = `
            <a href="/">Home</a>
            <a href="/static/new-booking.html" class="active">Book Repair</a>
            <a href="/static/track-ticket.html">Track Ticket</a>
            <a href="/static/login.html">Login</a>
        `;
        userInfo.innerHTML = '';
    }
}

// Auto-fill customer information if logged in
function autoFillCustomerInfo() {
    const customerName = localStorage.getItem('customer_name');
    const customerEmail = localStorage.getItem('customer_email');
    
    if (customerName && customerEmail) {
        // Fill the form fields
        document.getElementById('customerName').value = customerName;
        document.getElementById('customerEmail').value = customerEmail;
        
        // Make fields readonly
        document.getElementById('customerName').readOnly = true;
        document.getElementById('customerEmail').readOnly = true;
        
        // Add visual indicator that fields are auto-filled
        document.getElementById('customerName').style.backgroundColor = '#f0f0f0';
        document.getElementById('customerEmail').style.backgroundColor = '#f0f0f0';
    }
}

// Logout function
function logout() {
    localStorage.removeItem('customer_token');
    localStorage.removeItem('customer_id');
    localStorage.removeItem('customer_name');
    localStorage.removeItem('customer_email');
    window.location.href = '/static/login.html';
}
