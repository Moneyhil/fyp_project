import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { router } from 'expo-router';

const api = axios.create({
  baseURL: 'http://192.168.100.16:8000',
  timeout: 40000, 
  headers: {
    'Content-Type': 'application/json',
  },
});


api.interceptors.request.use( 
  async (config) => {
    try {
      const authToken = await AsyncStorage.getItem('authToken');
      console.log(' API Request:', config.method?.toUpperCase(), config.url);
      console.log('Auth token available:', authToken ? 'Yes' : 'No');
      
      if (authToken) {
        config.headers.Authorization = `Bearer ${authToken}`;
        console.log(' Authorization header set');
      } else {
        console.log(' No auth token found');
      }
    } catch (error) {
      console.error(' Error getting auth token:', error);
    }
    return config;
  },
  (error) => {
    console.error(' Request interceptor error:', error);
    return Promise.reject(error);
  }
);


api.interceptors.response.use(
  (response) => {
    console.log(' API Response:', response.status, response.config.url);
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    console.log(' API Error:', error.response?.status, originalRequest?.url);
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      console.log('Attempting token refresh...');
      originalRequest._retry = true;
      
      try {
        const refreshToken = await AsyncStorage.getItem('refreshToken');
        console.log('Refresh token available:', refreshToken ? 'Yes' : 'No');
        
        if (refreshToken) {
          const refreshResponse = await axios.post(
            `${api.defaults.baseURL}/donation/token/refresh/`,  
            { refresh: refreshToken }
          );
          
          console.log(' Token refresh successful:', refreshResponse.status);
          
          const { access } = refreshResponse.data;
          await AsyncStorage.setItem('authToken', access);
          
          originalRequest.headers.Authorization = `Bearer ${access}`;
          console.log(' Retrying original request with new token');
          return api(originalRequest);
        } else {
          console.log(' No refresh token available');
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError.response?.status, refreshError.response?.data);
        
        
        await AsyncStorage.multiRemove(['authToken', 'refreshToken', 'userInfo']);
        
        console.log(' Redirecting to login...');
        try {
          router.replace('/signin');
        } catch (navError) {
          console.error(' Navigation error:', navError);
        }
        
        return Promise.reject(new Error('Session expired. Please log in again.'));
      }
    }
    
    return Promise.reject(error);
  }
);

// Export API functions
export const getDonationRequests = () => api.get('/donation/requests/');
export const createProfile = (profileData) => api.post('/donation/profile/create/', profileData);
export const getProfile = (email) => api.get(`/donation/profile/${email}/`);
export const getMonthlyTracker = (email) => {
  if (!email || email === 'undefined' || email === 'null') {
    return Promise.reject(new Error('Invalid email parameter'));
  }
  
  const url = `/donation/monthly-tracker/?user_email=${encodeURIComponent(email)}`;
  return api.get(url);
};
export const createDonationRequest = (requestData) => api.post('/donation/donation-requests/create/', requestData);
export const createCallLog = (callData) => api.post('/donation/call-logs/create/', callData);
export const sendDonorNotification = (notificationData) => 
  api.post('/donation/messages/send-donor-notification/', notificationData);

export default api;
