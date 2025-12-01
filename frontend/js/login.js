// Unified Login JavaScript
// Handles both customer and admin authentication

let currentLoginType = 'customer';

// Tab switching
function showTab(type) {
    currentLoginType = type;
    
    const customerForm = document.getElementById('customerLoginForm');
    const adminForm = document.getElementById('adminLoginForm');
    const customerTab = document.getElementById('customerTab');
    const adminTab = document.getElementById('adminTab');
    
    if (type === 'customer') {
        customerForm.classList.remove('hidden');
        adminForm.classList.add('hidden');
        customerTab.classList.remove('btn-outline');
        customerTab.classList.add('btn-primary');
        adminTab.classList.remove('btn-primary');
        adminTab.classList.add('btn-outline');
    } else {
        customerForm.classList.add('hidden');
        adminForm.classList.remove('hidden');
        adminTab.classList.remove('btn-outline');
        adminTab.classList.add('btn-primary');
        customerTab.classList.remove('btn-primary');
        customerTab.classList.add('btn-outline');
    }
    
    // Clear errors
    document.getElementById('errorMessage').classList.add('hidden');
    document.getElementById('adminErrorMessage').classList.add('hidden');
}

// Customer Login
document.getElementById('customerLoginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const email = document.getElementById('customerEmail').value;
    const password = document.getElementById('customerPassword').value;
    const loginBtn = document.getElementById('loginBtn');
    const errorMessage = document.getElementById('errorMessage');
    
    errorMessage.classList.add('hidden');
    loginBtn.disabled = true;
    loginBtn.textContent = 'Signing in...';
    
    try {
        const response = await fetch('/api/v1/auth/customer/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
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
            showError(error.detail || 'Invalid email or password', 'customer');
            loginBtn.disabled = false;
            loginBtn.textContent = 'Sign In';
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('Network error. Please try again.', 'customer');
        loginBtn.disabled = false;
        loginBtn.textContent = 'Sign In';
    }
});

// Admin Login
document.getElementById('adminLoginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = document.getElementById('adminUsername').value;
    const password = document.getElementById('adminPassword').value;
    const loginBtn = document.getElementById('adminLoginBtn');
    const errorMessage = document.getElementById('adminErrorMessage');
    
    errorMessage.classList.add('hidden');
    loginBtn.disabled = true;
    loginBtn.textContent = 'Signing in...';
    
    try {
        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Store admin token and info
            localStorage.setItem('admin_token', data.access_token);
            localStorage.setItem('admin_username', data.admin_username);
            localStorage.setItem('admin_full_name', data.admin_full_name);
            
            // Redirect to admin dashboard
            window.location.href = '/static/admin.html';
        } else {
            const error = await response.json();
            showError(error.detail || 'Invalid username or password', 'admin');
            loginBtn.disabled = false;
            loginBtn.textContent = 'Sign In as Admin';
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('Network error. Please try again.', 'admin');
        loginBtn.disabled = false;
        loginBtn.textContent = 'Sign In as Admin';
    }
});

function showError(message, type) {
    if (type === 'customer') {
        const errorMessage = document.getElementById('errorMessage');
        const errorText = document.getElementById('errorText');
        errorText.textContent = message;
        errorMessage.classList.remove('hidden');
    } else {
        const errorMessage = document.getElementById('adminErrorMessage');
        const errorText = document.getElementById('adminErrorText');
        errorText.textContent = message;
        errorMessage.classList.remove('hidden');
    }
}

// Check if already logged in
window.addEventListener('DOMContentLoaded', function() {
    const customerToken = localStorage.getItem('customer_token');
    const adminToken = localStorage.getItem('admin_token');
    
    if (customerToken) {
        window.location.href = '/static/customer-portal.html';
    } else if (adminToken) {
        window.location.href = '/static/admin.html';
    }
});
