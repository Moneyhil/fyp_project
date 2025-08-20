// frontend1/constants/API.js
import axios from 'axios';

 const api = axios.create({
  baseURL: 'http://192.168.100.16:8000', // Django server computer IP address
  headers: {
    'Content-Type': 'application/json',
  },
});

// Donation Request APIs
export const createDonationRequest = (data) => {
  return api.post('/donation/donation-requests/', data);
};

export const getDonationRequests = () => {
  return api.get('/donation/donation-requests/');
};

export const respondToDonationRequest = (requestId, data) => {
  return api.post(`/donation/donation-requests/${requestId}/respond/`, data);
};

// Call Log APIs
export const createCallLog = (data) => {
  return api.post('/donation/call-logs/', data);
};

// Message APIs
export const getMessages = () => {
  return api.get('/donation/messages/');
};

export const markMessageAsRead = (messageId) => {
  return api.post(`/donation/messages/${messageId}/mark-read/`);
};

// Profile APIs
export const createProfile = (data) => {
  return api.post('/donation/profile/create/', data);
};

export const getProfile = (email) => {
  return api.get(`/donation/profile/${email}/`);
};

export default api;
