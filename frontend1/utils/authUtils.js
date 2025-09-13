import AsyncStorage from '@react-native-async-storage/async-storage';
import api from '../constants/API';

export const checkAuthStatus = async () => {
  try {
    const authToken = await AsyncStorage.getItem('authToken');
    const refreshToken = await AsyncStorage.getItem('refreshToken');
    const userInfo = await AsyncStorage.getItem('userInfo');

    if (!authToken || !userInfo) {
      return { isAuthenticated: false, user: null };
    }

    try {
      // Verify token
      const response = await api.post('/donation/token/verify/', {
        token: authToken
      });

      if (response.status === 200) {
        const user = JSON.parse(userInfo);
        return { isAuthenticated: true, user };
      }
    } catch (tokenError) {
      // Try to refresh token
      if (refreshToken) {
        try {
          const refreshResponse = await api.post('/donation/token/refresh/', {
            refresh: refreshToken
          });

          if (refreshResponse.status === 200) {
            const { access, refresh: newRefresh } = refreshResponse.data;
            await AsyncStorage.setItem('authToken', access);
            if (newRefresh) {
              await AsyncStorage.setItem('refreshToken', newRefresh);
            }
            
            const user = JSON.parse(userInfo);
            return { isAuthenticated: true, user };
          }
        } catch (refreshError) {
          await AsyncStorage.multiRemove(['authToken', 'refreshToken', 'userInfo']);
        }
      }
    }
  } catch (error) {
    console.error('Auth check error:', error);
  }
  
  return { isAuthenticated: false, user: null };
};

export const clearAuthData = async () => {
  await AsyncStorage.multiRemove(['authToken', 'refreshToken', 'userInfo']);
};

export const saveAuthData = async (authToken, refreshToken, userInfo) => {
  await AsyncStorage.setItem('authToken', authToken);
  await AsyncStorage.setItem('refreshToken', refreshToken);
  await AsyncStorage.setItem('userInfo', JSON.stringify(userInfo));
};



export const redirectBasedOnRole = (user, router) => {
  if (user.is_staff) {
    router.replace('/admindashboard');
  } else {
    router.replace('/home');
  }
};

export const getAuthToken = async () => {
  try {
    return await AsyncStorage.getItem('authToken');
  } catch (error) {
    console.error('Error getting auth token:', error);
    return null;
  }
};

export const handleApiError = (error, defaultMessage = 'An error occurred') => {
  let errorMessage = defaultMessage;
  
  if (error.response) {
    errorMessage = error.response.data?.error || 
                   error.response.data?.message || 
                   error.response.data?.non_field_errors?.[0] || 
                   defaultMessage;
  } else if (error.message) {
    errorMessage = error.message;
  }
  
  return errorMessage;
};