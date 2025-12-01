// Customer Signup JavaScript

document.getElementById('signupForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const signupBtn = document.getElementById('signupBtn');
    const errorMessage = document.getElementById('errorMessage');
    
    // Clear previous errors
    errorMessage.classList.add('hidden');
    
    // Validate passwords match
    if (password !== confirmPassword) {
        showError('Passwords do not match');
        return;
    }
    
    // Disable button and show loading state
    signupBtn.disabled = true;
    signupBtn.textContent = 'Creating Account...';
    
    try {
        const response = await fetch('/api/v1/auth/customer/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name,
                email,
                phone,
                password
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Store customer token and info
            localStorage.setItem('customer_token', data.access_token);
            localStorage.setItem('customer_id', data.customer_id);
            localStorage.setItem('customer_name', data.customer_name);
            localStorage.setItem('customer_email', data.customer_email);
            
            // Redirect to customer portal
            window.location.href = '/static/customer-portal.html';
        } else {
            const error = await response.json();
            showError(error.detail || 'Registration failed. Please try again.');
            
            // Re-enable button
            signupBtn.disabled = false;
            signupBtn.textContent = 'Create Account';
        }
    } catch (error) {
        console.error('Signup error:', error);
        showError('Network error. Please check your connection and try again.');
        
        // Re-enable button
        signupBtn.disabled = false;
        signupBtn.textContent = 'Create Account';
    }
});

function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    
    errorText.textContent = message;
    errorMessage.classList.remove('hidden');
}

// Check if already logged in
window.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('customer_token');
    if (token) {
        window.location.href = '/static/customer-portal.html';
    }
});
