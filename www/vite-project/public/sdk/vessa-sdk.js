/**
 * VESSA Security Incident Management SDK
 * @version 1.0.0
 */

class VessaClient {
  /**
   * Create a new VESSA client
   * @param {Object} options - Client options
   * @param {string} options.apiKey - Your VESSA API key
   * @param {string} [options.baseUrl='https://api.vessa.io'] - API base URL
   */
  constructor(options) {
    if (!options.apiKey) {
      throw new Error('API key is required');
    }
    
    this.apiKey = options.apiKey;
    this.baseUrl = options.baseUrl || 'https://api.vessa.io';
  }
  
  /**
   * Make an API request to the VESSA backend
   * @param {string} method - HTTP method (GET, POST, PUT, DELETE)
   * @param {string} path - API endpoint path
   * @param {Object} [data=null] - Request data (for POST, PUT)
   * @param {Object} [params=null] - Query parameters (for GET)
   * @returns {Promise<Object>} API response
   */
  async request(method, path, data = null, params = null) {
    let url = `${this.baseUrl}${path}`;
    
    // Add query parameters if provided
    if (params && method === 'GET') {
      const queryString = new URLSearchParams(params).toString();
      url = `${url}?${queryString}`;
    }
    
    const headers = {
      'Content-Type': 'application/json',
      'X-API-Key': this.apiKey,
    };
    
    const options = {
      method,
      headers,
      body: data && method !== 'GET' ? JSON.stringify(data) : undefined,
    };
    
    const response = await fetch(url, options);
    const responseData = await response.json();
    
    if (!response.ok) {
      const error = new Error(responseData.detail || 'API request failed');
      error.status = response.status;
      error.data = responseData;
      throw error;
    }
    
    return responseData;
  }
}

// Export the client
if (typeof module !== 'undefined') {
  module.exports = { VessaClient };
} else {
  window.VessaClient = VessaClient;
}