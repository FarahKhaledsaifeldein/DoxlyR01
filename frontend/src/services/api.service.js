// Example of proper API request configuration
const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Token ${localStorage.getItem('token')}`,  // If using token auth
    'X-CSRFToken': getCookie('csrftoken'),  // If using CSRF protection
};

// Example API call
async function makeApiCall(endpoint, method = 'GET', data = null) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: method,
            headers: headers,
            credentials: 'include',  // Important for cookies
            body: data ? JSON.stringify(data) : null,
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}