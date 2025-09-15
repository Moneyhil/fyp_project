import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Linking, Alert, Modal, ActivityIndicator, AppState } from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api, { createCallLog, sendDonorNotification } from '../constants/API';


export default function ShowProfileScreen() {
  const { donorData } = useLocalSearchParams();
  const donor = JSON.parse(donorData);
  const [showPostCallModal, setShowPostCallModal] = useState(false);
  const [donationRequestId, setDonationRequestId] = useState(null);
  const [callStartTime, setCallStartTime] = useState(null);
  const [userEmail, setUserEmail] = useState(null);
  const [callId, setCallId] = useState(null);
  const [isCallInProgress, setIsCallInProgress] = useState(false);

  const [donationTracker, setDonationTracker] = useState(null);
  const [loadingTracker, setLoadingTracker] = useState(true);

  useEffect(() => {
    const getUserEmail = async () => {
      try {
        const email = await AsyncStorage.getItem('userEmail');
        setUserEmail(email);
      } catch (error) {
      
    }
    };

    const fetchDonationTracker = async () => {
      try {
        const authToken = await AsyncStorage.getItem('authToken');
        if (!authToken) return;

        const response = await api.get(
          `/donation/donor-tracker/${donor.user}/`,
          {
            headers: { Authorization: `Bearer ${authToken}` },
          }
        );

        setDonationTracker(response.data);
      } catch (error) {
    
      } finally {
        setLoadingTracker(false);
      }
    };

    getUserEmail();
    if (donor?.user) fetchDonationTracker();
  }, [donor.user]);


  const handleCreateDonationRequest = async () => {
    try {
      const authToken = await AsyncStorage.getItem('authToken');
      if (!authToken) {
        Alert.alert('Error', 'Authentication required. Please log in again.');
        return null;
      }

      const response = await api.post('/donation/donation-requests/create/', {
        donor: donor.user,
        blood_group: donor.blood_group,
        notes: `Blood donation request for ${donor.blood_group} blood group`
      }, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      if (response && response.data && response.data.success) {
        return response.data.donation_request_id;
      } else {
        Alert.alert('Error', 'Invalid response from server');
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message || 'Failed to create donation request';
      Alert.alert('Error', errorMessage);
    }
    return null;
  };

  const logCall = async () => {
    try {
      const authToken = await AsyncStorage.getItem('authToken');
      if (!authToken) {
        return null;
      }

      const callData = {
        receiver: donor.user, 
        call_start_time: callStartTime,
        call_end_time: new Date().toISOString(),
      };

      const response = await createCallLog(callData, authToken);
      if (response && response.data && response.data.call_log && response.data.call_log.id) {
        const logId = response.data.call_log.id;
        setCallId(logId);
        return logId; 
      }
    } catch (error) {
      
    }
    return null;
  };

  const handleUserResponse = async (agreed) => {
    
    setShowPostCallModal(false);
    
    try {
      const loggedCallId = await logCall();
      
      if (donationRequestId) {
        const authToken = await AsyncStorage.getItem('authToken');
        if (!authToken) {
          Alert.alert('Error', 'Authentication required. Please log in again.');
          return;
        }
        
        await api.post(`/donation/donation-requests/${donationRequestId}/respond/`, {
          response: agreed,
          notes: agreed ? 'User confirmed need for blood donation' : 'User declined blood donation request'
        }, {
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        });
        
        if (agreed) {
          
          try {
            await sendDonorNotification({
              call_log_id: loggedCallId, 
              donor_agreed: true 
            });
            
            Alert.alert(
              'Success!',
              `${donor.full_name} has been notified about their agreement to donate blood to you. They will also receive an email confirmation request.`,
              [{ text: 'OK', onPress: () => router.back() }]
            );
            
          } catch (notificationError) {
            Alert.alert(
              'Partial Success',
              `Your response was recorded, but we couldn't send a notification to ${donor.full_name}. Please contact them directly.`,
              [{ text: 'OK', onPress: () => router.back() }]
            );
          }
        } else {
          
          Alert.alert(
            'Request Cancelled',
            'The donation request has been cancelled.',
            [{ text: 'OK', onPress: () => router.back() }]
          );
        }
      } else {
        
        router.back();
      }
    } catch (error) {
      console.error('Error in handleUserResponse:', error);
      Alert.alert(
        'Error', 
        'Failed to process your response. Please try again.',
        [{ text: 'OK', onPress: () => router.back() }]
      );
    }
  };



  const handleCall = async () => {
    const phoneNumber = donor.contact_number;
    if (phoneNumber) {
      await makeCall('dialer', phoneNumber);
    } else {
      Alert.alert('Error', 'Phone number not available');
    }
  };

  
  useEffect(() => {
    const handleAppStateChange = (nextAppState) => {
      if (isCallInProgress && nextAppState === 'active') {
    
        setTimeout(() => {
          setIsCallInProgress(false);
          setShowPostCallModal(true);
        }, 1000); 
      }
    };

    const subscription = AppState.addEventListener('change', handleAppStateChange);
    
    return () => {
      subscription?.remove();
    };
  }, [isCallInProgress]);

  const makeCall = async (method, phoneNumber) => {
    try {
      const requestId = await handleCreateDonationRequest();
      setDonationRequestId(requestId);
      setCallStartTime(new Date());
      setIsCallInProgress(true);
      
      
      Linking.openURL(`tel:${phoneNumber}`);
    } catch (error) {
      Alert.alert('Error', 'Failed to initiate call');
      setIsCallInProgress(false);
      setDonationRequestId(null);
      setCallStartTime(null);
    }
  };

  const PostCallModal = () => (
    <Modal
      visible={showPostCallModal}
      transparent={true}
      animationType="slide"
      onRequestClose={() => setShowPostCallModal(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <View style={styles.modalHeader}>
            <Ionicons name="call" size={24} color="#d40000" />
            <Text style={styles.modalTitle}>Call Completed</Text>
          </View>
          
          <Text style={styles.modalMessage}>
            Did {donor.full_name} agree to donate blood to you?
          </Text>
          
          <View style={styles.modalButtons}>
            <TouchableOpacity 
              style={[styles.modalButton, styles.noButton]} 
              onPress={() => handleUserResponse(false)}
            >
              <Text style={styles.noButtonText}>No</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={[styles.modalButton, styles.yesButton]} 
              onPress={() => handleUserResponse(true)}
            >
              <Text style={styles.yesButtonText}>Yes</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );



  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton} 
          onPress={() => router.back()}
        >
          <Ionicons name="arrow-back" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Profile</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.profileCard}>

          <View style={styles.infoSection}>
            <View style={styles.infoRow}>
              <View style={styles.infoItem}>
                <Ionicons name="person-outline" size={20} color="#666" />
                <View style={styles.infoTextContainer}>
                  <Text style={styles.infoLabel}>Full Name</Text>
                  <Text style={styles.infoValue}>{donor.full_name}</Text>
                </View>
              </View>
            </View>

            <View style={styles.infoRow}>
              <View style={styles.infoItem}>
                <Ionicons name="water-outline" size={20} color="#d40000" />
                <View style={styles.infoTextContainer}>
                  <Text style={styles.infoLabel}>Blood Group</Text>
                  <Text style={styles.infoValue}>{donor.blood_group}</Text>
                </View>
              </View>
            </View>

            <View style={styles.infoRow}>
              <View style={styles.infoItem}>
                <Ionicons name="location-outline" size={20} color="#666" />
                <View style={styles.infoTextContainer}>
                  <Text style={styles.infoLabel}>City</Text>
                  <Text style={styles.infoValue}>{donor.city}</Text>
                </View>
              </View>
            </View>

            <View style={styles.infoRow}>
              <View style={styles.infoItem}>
                <Ionicons name="call-outline" size={20} color="#666" />
                <View style={styles.infoTextContainer}>
                  <Text style={styles.infoLabel}>Contact Number</Text>
                  <Text style={styles.infoValue}>{donor.contact_number}</Text>
                </View>
              </View>
            </View>

            {donor.address && (
              <View style={styles.infoRow}>
                <View style={styles.infoItem}>
                  <Ionicons name="home-outline" size={20} color="#666" />
                  <View style={styles.infoTextContainer}>
                    <Text style={styles.infoLabel}>Address</Text>
                    <Text style={styles.infoValue}>{donor.address}</Text>
                  </View>
                </View>
              </View>
            )}

            {donor.gender && (
              <View style={styles.infoRow}>
                <View style={styles.infoItem}>
                  <Ionicons name="person-circle-outline" size={20} color="#666" />
                  <View style={styles.infoTextContainer}>
                    <Text style={styles.infoLabel}>Gender</Text>
                    <Text style={styles.infoValue}>{donor.gender}</Text>
                  </View>
                </View>
              </View>
            )}
          </View>
        </View>

    
        <View style={styles.trackerWrapper}>
          {loadingTracker ? (
            <ActivityIndicator size="large" color="#d40000" />
          ) : donationTracker ? (
            <View style={styles.donationCard}>
              <View style={styles.donationHeader}>
                <Text style={styles.donationTitle}>Donor Count</Text>
              </View>
              <View style={styles.donationContent}>
                <View style={styles.donationDisplay}>
                  <Text style={styles.donationNumber}>{donationTracker.completed_calls_count}</Text>
                  <Text style={styles.donationDivider}>/</Text>
                  <Text style={styles.donationLimit}>3</Text>
                </View>
                <Text
                  style={[
                    styles.donationStatus,
                    donationTracker.monthly_goal_completed && styles.completedStatus,
                  ]}
                >
                  {donationTracker.monthly_goal_completed
                    ? 'Monthly Goal Completed!' : 'In Progress'}
                </Text>
                {!donationTracker.monthly_goal_completed && (
                  <Text style={styles.donationSubtext}>
                    {3 - donationTracker.completed_calls_count} more donation
                    {3 - donationTracker.completed_calls_count !== 1 ? 's' : ''} to complete monthly goal
                  </Text>
                )}
              </View>
            </View>
          ) : (
            <Text style={{ textAlign: 'center', color: '#666' }}>
              No donation records found for this donor.
            </Text>
          )}
        </View>

        <View style={styles.emergencyNote}>
          <Ionicons name="information-circle" size={20} color="#ff6b35" />
          <Text style={styles.emergencyText}>
            Please be respectful when contacting donors. Only reach out in genuine emergencies.
          </Text>
        </View>
      </ScrollView>

      <View style={styles.actionButtons}>
        {!isCallInProgress ? (
          <TouchableOpacity style={styles.callButton} onPress={handleCall}>
            <Ionicons name="call" size={20} color="#fff" />
            <Text style={styles.buttonText}>Call Now</Text>
          </TouchableOpacity>
        ) : (
          <View style={styles.callInProgressContainer}>
            <ActivityIndicator size="small" color="#fff" style={{ marginRight: 8 }} />
            <Text style={styles.buttonText}>Call in Progress...</Text>
          </View>
        )}
      </View>
      
      <PostCallModal />
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
  emergencyNote: {
    backgroundColor: '#fff3e0',
    padding: 15,
    borderRadius: 10,
    flexDirection: 'row',
    alignItems: 'flex-start',
    borderLeftWidth: 4,
    borderLeftColor: '#ff6b35',
    marginBottom: 20,
  },
  emergencyText: {
    fontSize: 14,
    color: '#e65100',
    marginLeft: 10,
    flex: 1,
    lineHeight: 20,
  },
  actionButtons: {
    padding: 20,
  },

  callButton: {
    backgroundColor: '#d40000',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 25,
    margin: 20,
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 4,
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginLeft: 10,
  },
  modalMessage: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 25,
    lineHeight: 22,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 15,
  },
  modalButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  noButton: {
    backgroundColor: '#f5f5f5',
    borderWidth: 1,
    borderColor: '#ddd',
  },
  yesButton: {
    backgroundColor: '#d40000',
  },
  noButtonText: {
    color: '#666',
    fontSize: 16,
    fontWeight: '600',
  },
  yesButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  trackerWrapper: {
    marginBottom: 20,
  },
   donationCard: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    marginBottom: 20,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
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
  donationContent: { alignItems: 'center' },
  donationDisplay: { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
  donationNumber: { fontSize: 30 },
  donationDivider: { fontSize: 24, color: '#666', marginHorizontal: 8 },
  donationLimit: { fontSize: 24, color: '#666', fontWeight: '500' },
  completedStatus: { color: '#d40000' },
  donationMonth: { fontSize: 14, color: '#666', marginBottom: 8, fontWeight: '500' },
  donationSubtext: { fontSize: 14, color: '#666', textAlign: 'center' },
  completedMessage: { fontSize: 14, color: '#4caf50', textAlign: 'center', fontStyle: 'italic' },
});

