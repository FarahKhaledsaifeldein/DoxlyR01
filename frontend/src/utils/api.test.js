// Example test function for API connectivity
async function testApiConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health-check/`, {
            method: 'GET',
            headers: headers,
            credentials: 'include',
        });
        
        console.log('API Connection Test:', {
            status: response.status,
            ok: response.ok,
            headers: Object.fromEntries(response.headers),
        });
    } catch (error) {
        console.error('API Connection Test Failed:', error);
    }
}