// app/result.jsx
import React, { useEffect, useState } from "react";
import { View, Text, FlatList, StyleSheet, ActivityIndicator } from "react-native";
import { useLocalSearchParams } from "expo-router";
import api from '../constants/API';

export default function ResultScreen() {
  const { city, bloodGroup } = useLocalSearchParams();
  const [donors, setDonors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDonors();
  }, [city, bloodGroup]);

  const fetchDonors = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/donors/', {
        params: { city, blood_group: bloodGroup },
      });
      setDonors(response.data);
    } catch (error) {
      console.error("Error fetching donors:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#B71C1C" />
      </View>
    );
  }

  if (donors.length === 0) {
    return (
      <View style={styles.center}>
        <Text style={styles.noResults}>No donors found for your search.</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.heading}>
        Donors in {city} with blood group {bloodGroup}
      </Text>
      <FlatList
        data={donors}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.name}>{item.name}</Text>
            <Text style={styles.details}>📍 {item.city}</Text>
            <Text style={styles.details}>🩸 {item.blood_group}</Text>
            <Text style={styles.details}>📞 {item.phone_number}</Text>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
    padding: 15,
  },
  heading: {
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 10,
    color: "#B71C1C",
  },
  card: {
    backgroundColor: "#f8f8f8",
    padding: 15,
    marginBottom: 10,
    borderRadius: 8,
    elevation: 2,
  },
  name: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#333",
  },
  details: {
    fontSize: 14,
    color: "#555",
    marginTop: 2,
  },
  noResults: {
    fontSize: 16,
    color: "#999",
  },
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
});
