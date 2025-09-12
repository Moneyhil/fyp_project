import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api from '../constants/API';
import { checkAuthStatus } from '../utils/authUtils';

export default function ForgetPassword() {
  const [email, setEmail] = useState('');
  const router = useRouter();
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  useEffect(() => {
    checkAuthAndRedirect();
  }, []);

  const checkAuthAndRedirect = async () => {
    try {
      const { isAuthenticated, user } = await checkAuthStatus();
      
      if (isAuthenticated && user) {
        if (user.is_staff) {
          router.replace('/admindashboard');
        } else {
          router.replace('/home');
        }
        return;
      }
    } catch (error) {
      console.error('Auth check error:', error);
    } finally {
      setIsCheckingAuth(false);
    }
  };

  if (isCheckingAuth) {
    return null; // Show nothing while checking
  }

  const handleResetPassword = async () => {
    if (!email) {
      Alert.alert('Validation', 'Please enter your email');
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      Alert.alert('Validation', 'Please enter a valid email address');
      return;
    }

    try {
      const response = await api.post('/donation/forgot-password/', { 
        email: email.trim().toLowerCase() 
      });

      if (response.status === 200) {
        Alert.alert(
          'OTP Sent!', 
          response.data.message || 'A verification code has been sent to your email.',
          [
            {
              text: 'OK',
              onPress: () => router.push({ pathname: '/resetpassword', params: { email: email.trim().toLowerCase() } })
            }
          ]
        );
      }
    } catch (error) {
      console.error('Forgot password error:', error);
      
      let errorMessage = 'Network error occurred';
      if (error.response) {
        errorMessage = error.response.data?.error || error.response.data?.message || 'Failed to send reset code';
      }
      
      Alert.alert('Error', errorMessage);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Forgot Password?</Text>
      <Text style={styles.subtitle}>Enter your registered email address</Text>

      <TextInput
        style={styles.input}
        placeholder="Email Address"
        placeholderTextColor="#999"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />

      <TouchableOpacity style={styles.button} onPress={handleResetPassword}>
        <Text style={styles.buttonText}>Enter</Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={() => router.push('/signin')}>
        <Text style={styles.loginLink}>Back to Signin</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1, 
    justifyContent: 'center', 
    padding: 25, 
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 28, 
    fontWeight: 'bold', 
    marginBottom: 20, 
    textAlign: 'center',
    color: '#cc0000',
  },
  subtitle: {
    marginBottom: 10, 
    fontWeight: 'bold',
    color: '#333',
  },
  input: {
    width: '100%',
    borderRadius: 8,
    paddingHorizontal: 15,
    paddingVertical: 10,
    fontSize: 12,
    marginBottom: 5,
    backgroundColor: '#f2f2f2',
  },
  button: {
    backgroundColor: '#d40000',
    paddingVertical: 12,
    borderRadius: 25,
    marginTop: 20,
    marginBottom: 10,
    alignItems: 'center',
    shadowColor: '#d40000',
    shadowOffset: {
      width: 0,
      height: 3,
    },
    shadowOpacity: 1,
    shadowRadius: 6,
    elevation: 5,
  },
  buttonText: {
    color: '#fff', 
    fontWeight: 'bold', 
    fontSize: 16,
  },
  loginLink: {
    marginTop: 20, 
    color: '#3555e5ff',
    textAlign: 'center', 
    textDecorationLine: 'underline',
  },
});
