import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

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
            `${api.defaults.baseURL}/donation/token/refresh/`,  
            { refresh: refreshToken }
          );
          
          const { access } = refreshResponse.data;
          await AsyncStorage.setItem('authToken', access);
          
        
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
    
        await AsyncStorage.multiRemove(['authToken', 'refreshToken', 'userInfo']);
        
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
  console.log('getMonthlyTracker called with:', email, 'type:', typeof email);
  
  if (!email || email === 'undefined' || email === 'null') {
    console.error('Invalid email passed to getMonthlyTracker:', email);
    return Promise.reject(new Error('Invalid email parameter'));
  }
  
  const url = `/donation/monthly-tracker/?user_email=${encodeURIComponent(email)}`;
  console.log('Making request to URL:', url);
  
  return api.get(url);
};
export const createDonationRequest = (requestData) => api.post('/donation/donation-requests/create/', requestData);
export const createCallLog = (callData) => api.post('/donation/call-logs/create/', callData);
export const sendDonorNotification = (notificationData) => 
  api.post('/donation/messages/send-donor-notification/', notificationData);

export default api;
