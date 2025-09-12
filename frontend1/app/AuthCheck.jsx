import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator, StyleSheet, Text } from 'react-native';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api from '../constants/API';
import { checkAuthStatus, redirectBasedOnRole } from '../utils/authUtils';

export default function AuthCheck({ children }) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const { isAuthenticated, user } = await checkAuthStatus();
      
      if (isAuthenticated && user) {
        setIsAuthenticated(true);
        redirectBasedOnRole(user, router);
      } else {
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Auth check error:', error);
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

  if (!isAuthenticated) {
    // Redirect to upinscreen instead of returning null
    router.replace('/upinscreen');
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#d40000" />
        <Text>Redirecting...</Text>
      </View>
    );
  }

  return children;
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
});