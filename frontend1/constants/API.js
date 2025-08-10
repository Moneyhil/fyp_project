// frontend1/constants/API.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://192.168.1.17:8000', // Replace with your Django server's IP & port
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
