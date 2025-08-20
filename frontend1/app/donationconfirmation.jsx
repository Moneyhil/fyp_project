import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  Alert,
  TextInput,
} from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { respondToDonationRequest } from '../constants/API';

export default function DonationConfirmationScreen() {
  const { requestData, userType } = useLocalSearchParams();
  const request = JSON.parse(requestData);
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);

  const handleResponse = async (agreed) => {
    setLoading(true);
    try {
      const response = await respondToDonationRequest(request.id, {
        response: agreed,
        notes: notes || (agreed ? 'Agreed to donate blood' : 'Declined blood donation request')
      });

      if (response.data.success) {
        const message = agreed 
          ? 'Thank you! Your agreement to donate blood has been recorded and the requester has been notified.'
          : 'Your response has been recorded. The requester has been notified of your decision.';
        
        Alert.alert(
          agreed ? 'Donation Confirmed' : 'Response Recorded',
          message,
          [{ text: 'OK', onPress: () => router.back() }]
        );
      } else {
        Alert.alert('Error', 'Failed to record your response. Please try again.');
      }
    } catch (error) {
      console.error('Error responding to donation request:', error);
      Alert.alert('Error', 'Failed to record your response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getOtherUserName = () => {
    return userType === 'donor' ? request.requester_name : request.donor_name;
  };

  const getTitle = () => {
    return userType === 'donor' 
      ? 'Blood Donation Request'
      : 'Donation Request Status';
  };

  const getMessage = () => {
    if (userType === 'donor') {
      return `${request.requester_name} has requested you to donate ${request.blood_group} blood. Would you like to help them?`;
    } else {
      return `You have requested ${request.donor_name} to donate ${request.blood_group} blood. Please confirm if you still need this donation.`;
    }
  };

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
        <Text style={styles.headerTitle}>{getTitle()}</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Request Card */}
        <View style={styles.requestCard}>
          <View style={styles.requestHeader}>
            <Ionicons name="water" size={24} color="#d40000" />
            <Text style={styles.bloodGroup}>{request.blood_group}</Text>
          </View>
          
          <Text style={styles.requestMessage}>
            {getMessage()}
          </Text>

          {/* Request Details */}
          <View style={styles.detailsSection}>
            <View style={styles.detailRow}>
              <Ionicons name="person-outline" size={20} color="#666" />
              <Text style={styles.detailLabel}>Other Person:</Text>
              <Text style={styles.detailValue}>{getOtherUserName()}</Text>
            </View>
            
            <View style={styles.detailRow}>
              <Ionicons name="time-outline" size={20} color="#666" />
              <Text style={styles.detailLabel}>Urgency:</Text>
              <Text style={[styles.detailValue, styles.urgencyText]}>
                {request.urgency_level?.toUpperCase() || 'MEDIUM'}
              </Text>
            </View>
            
            <View style={styles.detailRow}>
              <Ionicons name="calendar-outline" size={20} color="#666" />
              <Text style={styles.detailLabel}>Requested:</Text>
              <Text style={styles.detailValue}>
                {new Date(request.created_at).toLocaleDateString()}
              </Text>
            </View>
          </View>

          {request.notes && (
            <View style={styles.notesSection}>
              <Text style={styles.notesLabel}>Additional Notes:</Text>
              <Text style={styles.notesText}>{request.notes}</Text>
            </View>
          )}
        </View>

        {/* Response Section */}
        <View style={styles.responseCard}>
          <Text style={styles.responseTitle}>Your Response</Text>
          
          <TextInput
            style={styles.notesInput}
            placeholder="Add any notes or comments (optional)"
            value={notes}
            onChangeText={setNotes}
            multiline
            numberOfLines={3}
            textAlignVertical="top"
          />
        </View>

        {/* Emergency Note */}
        <View style={styles.emergencyNote}>
          <Ionicons name="information-circle" size={20} color="#ff6b35" />
          <Text style={styles.emergencyText}>
            {userType === 'donor' 
              ? 'Blood donation is a noble act that can save lives. Please consider helping if you are able to donate.'
              : 'Please only confirm if you genuinely need blood donation. False requests waste valuable time and resources.'}
          </Text>
        </View>
      </ScrollView>

      {/* Action Buttons */}
      <View style={styles.actionButtons}>
        <TouchableOpacity 
          style={[styles.actionButton, styles.declineButton]} 
          onPress={() => handleResponse(false)}
          disabled={loading}
        >
          <Ionicons name="close" size={20} color="#666" />
          <Text style={styles.declineButtonText}>
            {userType === 'donor' ? 'Cannot Donate' : 'Cancel Request'}
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.actionButton, styles.confirmButton]} 
          onPress={() => handleResponse(true)}
          disabled={loading}
        >
          <Ionicons name="checkmark" size={20} color="#fff" />
          <Text style={styles.confirmButtonText}>
            {userType === 'donor' ? 'Agree to Donate' : 'Confirm Need'}
          </Text>
        </TouchableOpacity>
      </View>
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
  requestCard: {
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
  requestHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  bloodGroup: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#d40000',
    marginLeft: 10,
  },
  requestMessage: {
    fontSize: 16,
    color: '#333',
    lineHeight: 24,
    marginBottom: 20,
  },
  detailsSection: {
    gap: 12,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  detailLabel: {
    fontSize: 14,
    color: '#666',
    marginLeft: 8,
    marginRight: 8,
    minWidth: 80,
  },
  detailValue: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
    flex: 1,
  },
  urgencyText: {
    color: '#ff6b35',
    fontWeight: 'bold',
  },
  notesSection: {
    marginTop: 15,
    padding: 15,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
  },
  notesLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 5,
  },
  notesText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  responseCard: {
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
  responseTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 15,
  },
  notesInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    color: '#333',
    minHeight: 80,
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
    flexDirection: 'row',
    padding: 20,
    gap: 15,
  },
  actionButton: {
    flex: 1,
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
  declineButton: {
    backgroundColor: '#f5f5f5',
    borderWidth: 1,
    borderColor: '#ddd',
  },
  confirmButton: {
    backgroundColor: '#d40000',
  },
  declineButtonText: {
    color: '#666',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  confirmButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 8,
  },
});