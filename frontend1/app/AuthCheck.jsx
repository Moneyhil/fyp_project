import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api from '../constants/API';

export default function AuthCheck({ children }) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      // Get stored tokens and user info
      const authToken = await AsyncStorage.getItem('authToken');
      const refreshToken = await AsyncStorage.getItem('refreshToken');
      const userInfo = await AsyncStorage.getItem('userInfo');

      if (!authToken || !userInfo) {
        // No tokens stored, user needs to login
        setIsAuthenticated(false);
        setIsLoading(false);
        return;
      }

      try {
        // Try to verify the current token by making a test API call
        const user = JSON.parse(userInfo);
        
        // Set the authorization header for the test call
        const testResponse = await api.get('/donation/admin/users/', {
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        });

        // If the call succeeds, token is valid
        if (testResponse.status === 200) {
          setIsAuthenticated(true);
          // Redirect to appropriate dashboard based on user type
          if (user.is_staff) {
            router.replace('/admindashboard');
          } else {
            router.replace('/home');
          }
        }
      } catch (tokenError) {
        // Token might be expired, try to refresh it
        if (refreshToken) {
          try {
            const refreshResponse = await api.post('/donation/token/refresh/', {
              refresh: refreshToken
            });

            if (refreshResponse.status === 200) {
              // Update stored tokens
              const { access, refresh: newRefresh } = refreshResponse.data;
              await AsyncStorage.setItem('authToken', access);
              if (newRefresh) {
                await AsyncStorage.setItem('refreshToken', newRefresh);
              }

              setIsAuthenticated(true);
              // Redirect to appropriate dashboard
              const user = JSON.parse(userInfo);
              if (user.is_staff) {
                router.replace('/admindashboard');
              } else {
                router.replace('/home');
              }
            }
          } catch (refreshError) {
            // Refresh failed, clear stored data and require login
            await AsyncStorage.multiRemove(['authToken', 'refreshToken', 'userInfo']);
            setIsAuthenticated(false);
          }
        } else {
          // No refresh token, clear stored data and require login
          await AsyncStorage.multiRemove(['authToken', 'refreshToken', 'userInfo']);
          setIsAuthenticated(false);
        }
      }
    } catch (error) {
      console.error('Auth check error:', error);
      // On any error, clear stored data and require login
      await AsyncStorage.multiRemove(['authToken', 'refreshToken', 'userInfo']);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#d40000" />
      </View>
    );
  }

  // If authenticated, the user has already been redirected
  // If not authenticated, show the children (welcome screen)
  return !isAuthenticated ? children : null;
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
});