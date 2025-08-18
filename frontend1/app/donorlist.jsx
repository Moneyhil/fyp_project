import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  SafeAreaView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import axios from 'axios';

export default function DonorListScreen() {
  const { bloodGroup, city } = useLocalSearchParams();
  const [donors, setDonors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDonors();
  }, []);

  const fetchDonors = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `http://192.168.100.16:8000/donation/donors/search/?blood_group=${bloodGroup}&city=${city}`
      );
      setDonors(response.data.donors || []);
    } catch (error) {
      console.error('Error fetching donors:', error);
      Alert.alert('Error', 'Failed to fetch donor profiles. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderDonorItem = ({ item }) => (
    <TouchableOpacity 
      style={styles.donorCard}
      onPress={() => {
        router.push({
          pathname: '/showprofile',
          params: {
            donorData: JSON.stringify(item)
          }
        });
      }}
    >
      <View style={styles.donorInfo}>
        <Text style={styles.donorName}>{item.full_name}</Text>
        <Text style={styles.donorDetails}>Blood Group: {item.blood_group}</Text>
        <Text style={styles.donorDetails}>City: {item.city}</Text>
        <Text style={styles.donorDetails}>Contact: {item.contact_number}</Text>
        {item.address && (
          <Text style={styles.donorDetails}>Address: {item.address}</Text>
        )}
      </View>
      <View style={styles.bloodGroupBadge}>
        <Text style={styles.bloodGroupText}>{item.blood_group}</Text>
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity 
            style={styles.backButton} 
            onPress={() => router.back()}
          >
            <Text style={styles.backButtonText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>Donor List</Text>
        </View>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#d40000" />
          <Text style={styles.loadingText}>Loading donors...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton} 
          onPress={() => router.back()}
        >
          <Text style={styles.backButtonText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Donor List</Text>
      </View>
      
      {donors.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>No donors found</Text>
          <Text style={styles.emptySubtext}>
            No donors available for {bloodGroup} blood group in {city}.
          </Text>
          <TouchableOpacity 
            style={styles.searchAgainButton}
            onPress={() => router.back()}
          >
            <Text style={styles.searchAgainText}>Search Again</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={donors}
          renderItem={renderDonorItem}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.listContainer}
          showsVerticalScrollIndicator={false}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    backgroundColor: '#d40000',
    paddingVertical: 15,
    paddingHorizontal: 20,
    flexDirection: 'row',
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
  backButton: {
    marginRight: 15,
  },
  backButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    flex: 1,
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
  listContainer: {
    padding: 15,
  },
  donorCard: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    marginBottom: 15,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    borderLeftWidth: 4,
    borderLeftColor: '#d40000',
  },
  donorInfo: {
    flex: 1,
  },
  donorName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  donorDetails: {
    fontSize: 14,
    color: '#666',
    marginBottom: 3,
  },
  bloodGroupBadge: {
    backgroundColor: '#d40000',
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginLeft: 10,
  },
  bloodGroupText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  emptyText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  emptySubtext: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 20,
  },
  searchAgainButton: {
    backgroundColor: '#d40000',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 5,
  },
  searchAgainText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});