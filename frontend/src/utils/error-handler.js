function handleApiError(error) {
    console.error('API Error:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        url: error.response?.url
    });
    
    // Log detailed error information
    if (error.response) {
        console.log('Response:', error.response);
        console.log('Response Headers:', error.response.headers);
    }
}