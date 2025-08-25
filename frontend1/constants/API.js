import axios from 'axios';

 const api = axios.create({
  baseURL: 'http://192.168.100.16:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Donation Request APIs
export const createDonationRequest = (data) => {
  return api.post('/donation/donation-requests/create/', data);
};

export const getDonationRequests = () => {
  return api.get('/donation/donation-requests/');
};

export const respondToDonationRequest = (requestId, data) => {
  return api.post(`/donation/donation-requests/${requestId}/respond/`, data);
};

// Call Log APIs
export const createCallLog = (data, authToken) => {
  return api.post('/donation/call-logs/create/', data, {
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });
};

// Profile APIs
export const createProfile = (data) => {
  return api.post('/donation/profile/create/', data);
};

export const getProfile = (email) => {
  return api.get(`/donation/profile/${email}/`);
};

// Monthly Donation Tracker API
export const getMonthlyTracker = (userEmail) => {
  return api.get(`/donation/monthly-tracker/?user_email=${userEmail}`);
};

// Notification APIs
export const sendDonorNotification = (data) => {
  return api.post('/donation/messages/send-donor-notification/', data);
};

export default api;
