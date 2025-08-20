import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, ScrollView } from 'react-native';
import { router } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api from '../constants/API';

export default function HomeScreen() {
  const handleLogout = async () => {
    try {
      // Get refresh token from storage
      const refreshToken = await AsyncStorage.getItem('refreshToken');
      
      if (refreshToken) {
        // Send logout request to backend
        await api.post(
          '/donation/logout/',
          { refresh_token: refreshToken }
        );
      }
    } catch (error) {
      console.log('Logout API error:', error);
      // Continue with logout even if API call fails
    } finally {
      // Clear all tokens and user data from storage
      await AsyncStorage.multiRemove([
        'authToken',
        'refreshToken', 
        'user',
        'pendingVerificationEmail'
      ]);
      
      Alert.alert('Success', 'Logged out successfully!', [
        {
          text: 'OK',
          onPress: () => router.replace('/signin')
        }
      ]);
    }
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerText}>Blood Donation App</Text>
      </View>

      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Main Content */}
        <View style={styles.content}>
          {/* Buttons */}
          <TouchableOpacity style={styles.button} onPress={() => router.push('/usersprofile')}>
            <Text style={styles.buttonText}>Profile</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.button} onPress={() => router.push('/searchscreen')}>
            <Text style={styles.buttonText}>Need Blood</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.button} onPress={() => router.push('/about')}>
            <Text style={styles.buttonText}>About</Text>
          </TouchableOpacity>
        </View>

        {/* Logout Link at Bottom */}
        <View style={styles.logoutContainer}>
          <TouchableOpacity onPress={handleLogout}>
            <Text style={styles.logoutLinkText}>Logout</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    paddingTop: 50,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingBottom: 20,
  },
  header: {
    backgroundColor: '#d40000',
    width: '100%',
    paddingVertical: 15,
    alignItems: 'center',
    elevation: 5,
    shadowColor: '#2c0101',
    shadowOffset: {
      width: 0,
      height: 3,
    },
    shadowOpacity: 1,
    shadowRadius: 6,
  },
  headerText: {
    color: '#fff',
    fontSize: 22,
    fontWeight: 'bold',
  },
  content: {
    alignItems: 'center',
    paddingTop: 30,
    paddingBottom: 20,
  },
  button: {
    backgroundColor: '#ffebee',
    borderWidth: 1,
    borderColor: '#e53935',
    paddingVertical: 50,
    paddingHorizontal: 50,
    borderRadius: 10,
    marginVertical: 10,
    width: '80%',
    alignItems: 'center',
    shadowColor: '#b30b0b',
    shadowOffset: {
      width: 0,
      height: 3,
    },
    shadowOpacity: 1,
    shadowRadius: 6,
    elevation: 5,
  },
  buttonText: {
    color: '#d32f2f',
    fontSize: 18,
    fontWeight: 'bold',
  },
  logoutContainer: {
    alignItems: 'center',
    paddingVertical: 20,
    paddingHorizontal: 20,
  },
  logoutLinkText: {
    color: '#d32f2f',
    fontSize: 16,
    fontWeight: 'bold',
    textDecorationLine: 'underline',
    textAlign: 'center',
  },
});
