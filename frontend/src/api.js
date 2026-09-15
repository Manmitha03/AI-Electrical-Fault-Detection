// Simple API client configuration
const API_BASE_URL = 'http://localhost:8000/api';

export const endpoints = {
  devices: `${API_BASE_URL}/devices`,
  diagnoseSensor: `${API_BASE_URL}/diagnose`,
  diagnoseImage: `${API_BASE_URL}/diagnose/image`,
  chatbot: `${API_BASE_URL}/chat`,
  alerts: `${API_BASE_URL}/alerts`,
  demoScenarios: `${API_BASE_URL}/demo/scenarios`,
  demoScenarioActivate: `${API_BASE_URL}/demo/scenario`,
  demoReset: `${API_BASE_URL}/demo/reset`,
  statistics: `${API_BASE_URL}/statistics`,
};

export const wsEndpoint = 'ws://localhost:8000/ws/sensors';

export const fetchApi = async (url, options = {}) => {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Request failed:', error);
    throw error;
  }
};
