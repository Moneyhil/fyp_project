import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  FlatList,
  Alert,
  RefreshControl,
} from 'react-native';
import { router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { getMessages, markMessageAsRead } from '../constants/API';

export default function MessagesScreen() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchMessages = async () => {
    try {
      const response = await getMessages();
      if (response.data.success) {
        setMessages(response.data.messages);
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
      Alert.alert('Error', 'Failed to load messages');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const markAsRead = async (messageId) => {
    try {
      await markMessageAsRead(messageId);
      // Update local state
      setMessages(prevMessages => 
        prevMessages.map(msg => 
          msg.id === messageId ? { ...msg, is_read: true } : msg
        )
      );
    } catch (error) {
      console.error('Error marking message as read:', error);
    }
  };

  const handleMessagePress = async (message) => {
    if (!message.is_read) {
      await markAsRead(message.id);
    }

    // Navigate to donation confirmation if it's a donation request
    if (message.donation_request && message.message_type === 'alert') {
      router.push({
        pathname: '/donationconfirmation',
        params: {
          requestData: JSON.stringify(message.donation_request),
          userType: 'donor' // Since this is an alert to a donor
        }
      });
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchMessages();
  };

  useEffect(() => {
    fetchMessages();
  }, []);

  const getMessageIcon = (messageType) => {
    switch (messageType) {
      case 'alert':
        return 'notifications';
      case 'confirmation':
        return 'checkmark-circle';
      case 'reminder':
        return 'time';
      default:
        return 'mail';
    }
  };

  const getMessageIconColor = (messageType) => {
    switch (messageType) {
      case 'alert':
        return '#ff6b35';
      case 'confirmation':
        return '#4caf50';
      case 'reminder':
        return '#2196f3';
      default:
        return '#666';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) {
      return 'Today';
    } else if (diffDays === 2) {
      return 'Yesterday';
    } else if (diffDays <= 7) {
      return `${diffDays - 1} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const renderMessage = ({ item }) => (
    <TouchableOpacity 
      style={[styles.messageCard, !item.is_read && styles.unreadMessage]} 
      onPress={() => handleMessagePress(item)}
    >
      <View style={styles.messageHeader}>
        <View style={styles.messageIconContainer}>
          <Ionicons 
            name={getMessageIcon(item.message_type)} 
            size={20} 
            color={getMessageIconColor(item.message_type)} 
          />
        </View>
        <View style={styles.messageInfo}>
          <Text style={[styles.messageSubject, !item.is_read && styles.unreadText]}>
            {item.subject}
          </Text>
          <Text style={styles.messageSender}>
            From: {item.sender_name}
          </Text>
        </View>
        <View style={styles.messageTime}>
          <Text style={styles.timeText}>{formatDate(item.created_at)}</Text>
          {!item.is_read && <View style={styles.unreadDot} />}
        </View>
      </View>
      
      <Text style={styles.messageContent} numberOfLines={2}>
        {item.content}
      </Text>
      
      {item.message_type === 'alert' && (
        <View style={styles.actionHint}>
          <Ionicons name="arrow-forward" size={16} color="#d40000" />
          <Text style={styles.actionHintText}>Tap to respond</Text>
        </View>
      )}
    </TouchableOpacity>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Ionicons name="mail-outline" size={64} color="#ccc" />
      <Text style={styles.emptyStateTitle}>No Messages</Text>
      <Text style={styles.emptyStateText}>
        You'll receive notifications here when someone requests blood donation or responds to your requests.
      </Text>
    </View>
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
        <Text style={styles.headerTitle}>Messages</Text>
        <TouchableOpacity 
          style={styles.refreshButton} 
          onPress={onRefresh}
        >
          <Ionicons name="refresh" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      <FlatList
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.messagesList}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={!loading ? renderEmptyState : null}
      />
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
  refreshButton: {
    padding: 5,
  },
  messagesList: {
    padding: 20,
    flexGrow: 1,
  },
  messageCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  unreadMessage: {
    borderLeftWidth: 4,
    borderLeftColor: '#d40000',
    backgroundColor: '#fff8f8',
  },
  messageHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  messageIconContainer: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#f5f5f5',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  messageInfo: {
    flex: 1,
  },
  messageSubject: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  unreadText: {
    fontWeight: 'bold',
  },
  messageSender: {
    fontSize: 12,
    color: '#666',
  },
  messageTime: {
    alignItems: 'flex-end',
  },
  timeText: {
    fontSize: 12,
    color: '#999',
  },
  unreadDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#d40000',
    marginTop: 4,
  },
  messageContent: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 8,
  },
  actionHint: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  actionHintText: {
    fontSize: 12,
    color: '#d40000',
    fontWeight: '600',
    marginLeft: 4,
  },
  emptyState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyStateTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#999',
    marginTop: 16,
    marginBottom: 8,
  },
  emptyStateText: {
    fontSize: 14,
    color: '#ccc',
    textAlign: 'center',
    lineHeight: 20,
    paddingHorizontal: 40,
  },
});