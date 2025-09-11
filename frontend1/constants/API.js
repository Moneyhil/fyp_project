import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const api = axios.create({
  baseURL: 'http://192.168.100.16:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    try {
      const authToken = await AsyncStorage.getItem('authToken');
      if (authToken) {
        config.headers.Authorization = `Bearer ${authToken}`;
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = await AsyncStorage.getItem('refreshToken');
        if (refreshToken) {
          const refreshResponse = await axios.post(
            'http://192.168.100.16:8000/donation/token/refresh/',
            { refresh: refreshToken }
          );
          
          const { access } = refreshResponse.data;
          await AsyncStorage.setItem('authToken', access);
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        await AsyncStorage.multiRemove(['authToken', 'refreshToken', 'userInfo']);
        // You might want to emit an event here to redirect to login
      }
    }
    
    return Promise.reject(error);
  }
);

// Export API functions
export const getDonationRequests = () => api.get('/donation/requests/');
export const createProfile = (profileData) => api.post('/donation/profile/', profileData);
export const getProfile = () => api.get('/donation/profile/');
export const getMonthlyTracker = () => api.get('/donation/monthly-tracker/');
export const createDonationRequest = (requestData) => api.post('/donation/requests/', requestData);
export const createCallLog = (callData) => api.post('/donation/call-logs/', callData);
export const respondToDonationRequest = (requestId, responseData) => 
  api.patch(`/donation/requests/${requestId}/`, responseData);
export const sendDonorNotification = (notificationData) => 
  api.post('/donation/notifications/', notificationData);

export default api;
