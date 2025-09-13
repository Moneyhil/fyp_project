import React, { useEffect, useState } from 'react';
import {  View, Text, StyleSheet, ActivityIndicator} from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import api from '../constants/API';

export default function ConfirmDonationScreen() {
  const { call_id, response } = useLocalSearchParams();
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (call_id && response) {
      handleConfirmation();
    } else {
      setMessage('Invalid confirmation link');
      setLoading(false);
    }
  }, [call_id, response]);

  const handleConfirmation = async () => {
    try {
      setLoading(true);
      
    
      const apiResponse = await api.get(
        `/donation/confirm-donation/?call_log_id=${call_id}&response=${response}`
      );
      
      if (apiResponse.data.success) {
        setSuccess(true);
        // Use the personalized message from backend
        setMessage(apiResponse.data.message || 'Thank you for your response!');
      } else {
        setMessage(apiResponse.data.message || 'Failed to process confirmation');
      }
    } catch (error) {
      console.error('Confirmation error:', error);
      setMessage('Failed to process your confirmation. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Donation Confirmation</Text>
        
        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#d40000" />
            <Text style={styles.loadingText}>Processing your response...</Text>
          </View>
        ) : (
          <View style={styles.messageContainer}>
            <Text style={[styles.message, success ? styles.successMessage : styles.errorMessage]}>
              {message}
            </Text>
          </View>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#d40000',
    marginBottom: 30,
    textAlign: 'center',
  },
  loadingContainer: {
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 15,
    fontSize: 16,
    color: '#666',
  },
  messageContainer: {
    alignItems: 'center',
  },
  message: {
    fontSize: 16,
    textAlign: 'center',
    lineHeight: 24,
  },
  successMessage: {
    color: '#28a745',
  },
  errorMessage: {
    color: '#dc3545',
  },
});