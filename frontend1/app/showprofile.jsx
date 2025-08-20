import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  Linking,
  Alert,
  Modal,
} from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import api, { createDonationRequest, createCallLog, respondToDonationRequest } from '../constants/API';

export default function ShowProfileScreen() {
  const { donorData } = useLocalSearchParams();
  const donor = JSON.parse(donorData);
  const [showPostCallModal, setShowPostCallModal] = useState(false);
  const [donationRequestId, setDonationRequestId] = useState(null);
  const [callStartTime, setCallStartTime] = useState(null);

  const createDonationRequest = async () => {
    try {
      const response = await createDonationRequest({
        donor_id: donor.id,
        blood_group: donor.blood_group,
        urgency_level: 'medium',
        notes: `Blood donation request for ${donor.blood_group} blood group`
      });
      
      if (response.data.success) {
        return response.data.data.id;
      }
    } catch (error) {
      console.error('Error creating donation request:', error);
      Alert.alert('Error', 'Failed to create donation request');
    }
    return null;
  };

  const logCall = async (duration, outcome) => {
    try {
      await createCallLog({
        donor_id: donor.id,
        duration: duration,
        outcome: outcome,
        notes: `Call to ${donor.full_name} regarding blood donation`
      });
    } catch (error) {
      console.error('Error logging call:', error);
    }
  };

  const handleUserResponse = async (agreed) => {
    try {
      if (donationRequestId) {
        await respondToDonationRequest(donationRequestId, {
          response: agreed,
          notes: agreed ? 'User confirmed need for blood donation' : 'User declined blood donation request'
        });
        
        if (agreed) {
          Alert.alert(
            'Request Sent',
            `A donation request has been sent to ${donor.full_name}. They will receive a message asking if they agree to donate blood to you.`,
            [{ text: 'OK', onPress: () => router.back() }]
          );
        } else {
          Alert.alert(
            'Request Cancelled',
            'The donation request has been cancelled.',
            [{ text: 'OK', onPress: () => router.back() }]
          );
        }
      }
    } catch (error) {
      console.error('Error responding to donation request:', error);
      Alert.alert('Error', 'Failed to process your response');
    }
    setShowPostCallModal(false);
  };

  const handleCall = async () => {
    const phoneNumber = donor.contact_number;
    if (phoneNumber) {
      Alert.alert(
        'Make a Call',
        `Do you want to call ${donor.full_name} at ${phoneNumber}?`,
        [
          {
            text: 'Cancel',
            style: 'cancel',
          },
          {
            text: 'Call',
            onPress: async () => {
              // Create donation request before making the call
              const requestId = await createDonationRequest();
              setDonationRequestId(requestId);
              setCallStartTime(new Date());
              
              // Make the call
              Linking.openURL(`tel:${phoneNumber}`);
              
              // Show post-call modal after a delay (simulating call end)
              setTimeout(() => {
                setShowPostCallModal(true);
              }, 3000); // 3 second delay to simulate call
            },
          },
        ]
      );
    } else {
      Alert.alert('Error', 'Phone number not available');
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
    <SafeAreaView style={styles.container}>
      {/* Header */}
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
        {/* Profile Card */}
        <View style={styles.profileCard}>


          {/* Information Section */}
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

        {/* Emergency Note */}
        <View style={styles.emergencyNote}>
          <Ionicons name="information-circle" size={20} color="#ff6b35" />
          <Text style={styles.emergencyText}>
            Please be respectful when contacting donors. Only reach out in genuine emergencies.
          </Text>
        </View>
      </ScrollView>

      {/* Action Button */}
      <View style={styles.actionButtons}>
        <TouchableOpacity style={styles.callButton} onPress={handleCall}>
          <Ionicons name="call" size={20} color="#fff" />
          <Text style={styles.buttonText}>Call Now</Text>
        </TouchableOpacity>
      </View>
      
      <PostCallModal />
    </SafeAreaView>
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
});