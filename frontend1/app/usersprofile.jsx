import React, { useState, useEffect, useCallback } from 'react';
import { View, Text,  StyleSheet,  TouchableOpacity,  ActivityIndicator} from 'react-native';
import { router, useFocusEffect } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api, { getProfile, getMonthlyTracker } from '../constants/API';
import { Ionicons } from '@expo/vector-icons';

export default function UsersProfileScreen() {
  const [profileData, setProfileData] = useState(null);
  const [donationTracker, setDonationTracker] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

const extractEmail = (user) => {
  const possibleKeys = ["email", "userEmail", "User_email", "emailAddress", "user_email"];
  for (let key of possibleKeys) {
    if (user[key] && typeof user[key] === "string" && user[key].includes("@")) {
      return user[key];
    }
  }
  return null;
};

  useFocusEffect(
    useCallback(() => {
      fetchUserProfile();
    }, [])
  );

  const handleAuthError = async (errorMessage = 'Session expired. Please log in again.') => {
    try {
      await AsyncStorage.multiRemove(['authToken', 'refreshToken', 'userInfo']);
      setError(errorMessage);
      
      setTimeout(() => {
        router.replace('/login');
      }, 1000);
    } catch (error) {
      console.error('Error clearing auth data:', error);
    }
  };
  
  
  const fetchUserProfile = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const userString = await AsyncStorage.getItem('userInfo');
      if (!userString) {
        await handleAuthError('No user data found. Please log in again.');
        return;
      }
  
      const user = JSON.parse(userString);
      const email = extractEmail(user);
  
      if (!email || email === 'undefined' || email === 'null') {
        console.error('No valid email found in user object:', user);
        await handleAuthError('User email not found. Please log in again.');
        return;
      }
      
      if (typeof email !== 'string' || !email.includes('@')) {
        console.error('Invalid email format:', email);
        await handleAuthError('Invalid email format. Please log in again.');
        return;
      }
  
      try {
        const profileResponse = await getProfile(email);
        if (profileResponse.status === 200) {
          setProfileData(profileResponse.data.profile);
        }
      } catch (profileError) {
        console.error('Profile fetch error:', profileError);
        if (profileError.response?.status === 401 || 
            profileError.message === 'Session expired. Please log in again.') {
          await handleAuthError('Session expired. Please log in again.');
          return;
        } else if (profileError.response?.status === 404) {
          setError('Profile not found. Please create your profile first.');
        } else {
          setError('Failed to load profile. Please try again.');
        }
        setLoading(false);
        return;
      }
  
      try {
        console.log('Calling getMonthlyTracker with email:', email);
        
        if (!email || email.trim() === '' || email === 'undefined') {
          console.warn('Email validation failed before API call:', email);
          return;
        }
        
        const monthlyResponse = await getMonthlyTracker(email.trim());
        console.log('Monthly tracker response:', monthlyResponse);
        
        if (monthlyResponse.status === 200) {
          if (monthlyResponse.data) {
            setDonationTracker(monthlyResponse.data);
            console.log('Monthly tracker data set:', monthlyResponse.data);
          } else {
            console.warn('Monthly tracker response has no data');
          }
        } else {
          console.warn('Monthly tracker response status:', monthlyResponse.status);
        }
      } catch (monthlyError) {
        console.error('Monthly tracker fetch failed:', monthlyError);
        
        if (monthlyError.response?.status === 401 || 
            monthlyError.message === 'Session expired. Please log in again.') {
          await handleAuthError('Session expired. Please log in again.');
          return;
        }
        console.error('Error details:', {
          message: monthlyError.message,
          response: monthlyError.response?.data,
          status: monthlyError.response?.status,
          url: monthlyError.config?.url
        });
      }
      
    } catch (error) {
      console.error('General fetch error:', error);
      if (error.message === 'Session expired. Please log in again.') {
        await handleAuthError();
        return;
      }
      setError('Failed to load data. Please try again.');
    } finally {
      setLoading(false);
    }
  };



  if (loading) {
    return (
      <View style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#d40000" />
          <Text style={styles.loadingText}>Loading your profile...</Text>
        </View>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity 
            style={styles.backButton} 
            onPress={() => router.back()}
          >
            <Ionicons name="arrow-back" size={24} color="#fff" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>My Profile</Text>
          <View style={styles.placeholder} />
        </View>
        
        <View style={styles.errorContainer}>
          <Ionicons name="person-circle-outline" size={80} color="#ccc" />
          <Text style={styles.errorText}>{error}</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton} 
          onPress={() => router.back()}
        >
          <Ionicons name="arrow-back" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>My Profile</Text>
        <View style={styles.placeholder} />
      </View>

      <View style={styles.content}>
        
        <View style={styles.profileCard}>
          
          <View style={styles.infoSection}>
            <View style={styles.infoRow}>
              <View style={styles.infoItem}>
                <Ionicons name="person-outline" size={20} color="#666" />
                <View style={styles.infoTextContainer}>
                  <Text style={styles.infoLabel}>Full Name</Text>
                  <Text style={styles.infoValue}>
                    {profileData?.first_name} {profileData?.last_name}
                  </Text>
                </View>
              </View>
            </View>

            <View style={styles.infoRow}>
              <View style={styles.infoItem}>
                <Ionicons name="water-outline" size={20} color="#666" />
                <View style={styles.infoTextContainer}>
                  <Text style={styles.infoLabel}>Blood Group</Text>
                  <Text style={styles.infoValue}>{profileData?.blood_group}</Text>
                </View>
              </View>
            </View>

            <View style={styles.infoRow}>
              <View style={styles.infoItem}>
                <Ionicons name="location-outline" size={20} color="#666" />
                <View style={styles.infoTextContainer}>
                  <Text style={styles.infoLabel}>City</Text>
                  <Text style={styles.infoValue}>{profileData?.city}</Text>
                </View>
              </View>
            </View>

            <View style={styles.infoRow}>
              <View style={styles.infoItem}>
                <Ionicons name="call-outline" size={20} color="#666" />
                <View style={styles.infoTextContainer}>
                  <Text style={styles.infoLabel}>Contact Number</Text>
                  <Text style={styles.infoValue}>{profileData?.contact_number}</Text>
                </View>
              </View>
            </View>

            {profileData?.address && (
              <View style={styles.infoRow}>
                <View style={styles.infoItem}>
                  <Ionicons name="home-outline" size={20} color="#666" />
                  <View style={styles.infoTextContainer}>
                    <Text style={styles.infoLabel}>Address</Text>
                    <Text style={styles.infoValue}>{profileData?.address}</Text>
                  </View>
                </View>
              </View>
            )}

            {profileData?.gender && (
              <View style={styles.infoRow}>
                <View style={styles.infoItem}>
                  <Ionicons name="person-circle-outline" size={20} color="#666" />
                  <View style={styles.infoTextContainer}>
                    <Text style={styles.infoLabel}>Gender</Text>
                    <Text style={styles.infoValue}>
                      {profileData?.gender?.charAt(0).toUpperCase() + profileData?.gender?.slice(1)}
                    </Text>
                  </View>
                </View>
              </View>
            )}

            {profileData?.role && (
              <View style={styles.infoRow}>
                <View style={styles.infoItem}>
                  <Ionicons name="medical-outline" size={20} color="#666" />
                  <View style={styles.infoTextContainer}>
                    <Text style={styles.infoLabel}>Role</Text>
                    <Text style={styles.infoValue}>
                      {profileData?.role?.charAt(0).toUpperCase() + profileData?.role?.slice(1)}
                    </Text>
                  </View>
                </View>
              </View>
            )}
          </View>
        </View>

        
        {donationTracker && (
          <View style={styles.donationCard}>
            <View style={styles.donationHeader}>
              <Ionicons name="heart" size={24} color="#d40000" />
              <Text style={styles.donationTitle}>Monthly Donation Progress</Text>
            </View>
            
            <View style={styles.donationContent}>
              <View style={styles.donationDisplay}>
                <Text style={styles.donationNumber}>{donationTracker.completed_calls_count}</Text>
                <Text style={styles.donationDivider}>/</Text>
                <Text style={styles.donationLimit}>3</Text>
              </View>
              
              <Text style={[styles.donationStatus, donationTracker.monthly_goal_completed && styles.completedStatus]}>
                {donationTracker.monthly_goal_completed ? "Monthly Goal Completed!" : "Donations This Month"}
              </Text>
              
              <Text style={styles.donationMonth}>
                {donationTracker.month}
              </Text>
              
              {!donationTracker.monthly_goal_completed && (
                <Text style={styles.donationSubtext}>
                  {3 - donationTracker.completed_calls_count} more donation{3 - donationTracker.completed_calls_count !== 1 ? 's' : ''} to complete monthly goal
                </Text>
              )}
              
              {donationTracker.monthly_goal_completed && donationTracker.goal_completed_at && (
                <Text style={styles.completedMessage}>
                  Completed on {new Date(donationTracker.goal_completed_at).toLocaleDateString()}
                </Text>
              )}
            </View>
          </View>
        )}

      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    backgroundColor: '#d40000',
    paddingVertical: 15,
    paddingHorizontal: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    elevation: 5,
    shadowColor: '#2c0101',
    shadowOffset: {
      width: 0,
      height: 3,
    },
    shadowOpacity: 1,
    shadowRadius: 6,
  },
  backButton: {
    padding: 5,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
  },
  placeholder: {
    width: 34,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginVertical: 20,
  },

  content: {
    flex: 1,
    padding: 20,
  },
  profileCard: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    marginBottom: 20,
  },
  infoSection: {
    gap: 15,
  },
  infoRow: {
    flexDirection: 'row',
  },
  infoItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    flex: 1,
  },
  infoTextContainer: {
    marginLeft: 12,
    flex: 1,
  },
  infoLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  infoValue: {
    fontSize: 16,
    color: '#333',
    fontWeight: '500',
  },
  donationCard: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    marginBottom: 20,
  },
  donationHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  donationTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginLeft: 10,
  },
  donationContent: {
    alignItems: 'center',
  },
  donationDisplay: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  donationNumber: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#d40000',
  },
  donationDivider: {
    fontSize: 24,
    color: '#666',
    marginHorizontal: 8,
  },
  donationLimit: {
    fontSize: 24,
    color: '#666',
    fontWeight: '500',
  },
  donationStatus: {
    fontSize: 16,
    fontWeight: '600',
    color: '#4caf50',
    marginBottom: 5,
  },
  completedStatus: {
    color: '#d40000',
  },
  donationMonth: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
    fontWeight: '500',
  },
  donationSubtext: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  completedMessage: {
    fontSize: 14,
    color: '#4caf50',
    textAlign: 'center',
    fontStyle: 'italic',
  },


});