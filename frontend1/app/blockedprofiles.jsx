import React, { useState, useEffect } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Alert, ScrollView, RefreshControl, SafeAreaView } from "react-native";
import { useRouter } from "expo-router";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Ionicons } from "@expo/vector-icons";
import api from "../constants/API";

export default function BlockedProfiles() {
  const router = useRouter();
  const [blockedUsers, setBlockedUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadBlockedUsers();
  }, []);

  const loadBlockedUsers = async () => {
    try {
      const token = await AsyncStorage.getItem("authToken");
      const response = await api.get("/donation/admin/users/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.status === 200) {
        // Filter only blocked users (is_active = false)
        const blocked = response.data.users.filter(user => !user.is_active);
        setBlockedUsers(blocked);
      }
    } catch (error) {
      console.error("Load blocked users error:", error);
      Alert.alert("Error", "Failed to load blocked users");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadBlockedUsers();
  };

  const unblockUser = async (userId) => {
    Alert.alert(
      "Unblock User",
      "Are you sure you want to unblock this user?",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Unblock",
          onPress: async () => {
            try {
              const token = await AsyncStorage.getItem("authToken");
              const response = await api.post(
                `/donation/admin/users/${userId}/block/`,
                {},
                {
                  headers: {
                    Authorization: `Bearer ${token}`,
                  },
                }
              );

              if (response.status === 200) {
                Alert.alert("Success", "User unblocked successfully");
                loadBlockedUsers(); // Refresh the list
              }
            } catch (error) {
              console.error("Unblock error:", error);
              Alert.alert("Error", "Failed to unblock user");
            }
          },
        },
      ]
    );
  };

  const deleteUser = async (userId) => {
    Alert.alert(
      "Delete User",
      "Are you sure you want to delete this user? This action cannot be undone.",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Delete",
          style: "destructive",
          onPress: async () => {
            try {
              const token = await AsyncStorage.getItem("authToken");
              const response = await api.delete(
                `/donation/admin/users/${userId}/delete/`,
                {
                  headers: {
                    Authorization: `Bearer ${token}`,
                  },
                }
              );

              if (response.status === 200) {
                Alert.alert("Success", "User deleted successfully");
                loadBlockedUsers(); // Refresh the list
              }
            } catch (error) {
              console.error("Delete user error:", error);
              Alert.alert("Error", "Failed to delete user");
            }
          },
        },
      ]
    );
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity 
            style={styles.backButton} 
            onPress={() => router.back()}
          >
            <Ionicons name="arrow-back" size={24} color="#fff" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Blocked Profiles</Text>
          <View style={styles.placeholder} />
        </View>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading blocked users...</Text>
        </View>
      </SafeAreaView>
    );
  }

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
        <Text style={styles.headerTitle}>Blocked Profiles</Text>
        <View style={styles.placeholder} />
      </View>

      {/* Content */}
      <View style={styles.content}>
        {blockedUsers.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Ionicons name="ban-outline" size={80} color="#ccc" />
            <Text style={styles.emptyText}>No blocked users found</Text>
            <Text style={styles.emptySubtext}>All users are currently active</Text>
          </View>
        ) : (
          <>
            <View style={styles.statsHeader}>
              <Text style={styles.statsText}>
                {blockedUsers.length} blocked user{blockedUsers.length !== 1 ? 's' : ''}
              </Text>
            </View>
            
            <ScrollView
              style={styles.usersList}
              refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
            >
              {blockedUsers.map((user) => (
                <View key={user.id} style={styles.userCard}>
                  <View style={styles.userInfo}>
                    <Text style={styles.userName}>{user.name}</Text>
                    <Text style={styles.userEmail}>{user.email}</Text>
                    <View style={styles.userStatus}>
                      <Text style={styles.blockedBadge}>Blocked</Text>
                      <Text style={[styles.statusBadge, user.is_verified ? styles.verifiedBadge : styles.unverifiedBadge]}>
                        {user.is_verified ? "Verified" : "Unverified"}
                      </Text>
                    </View>
                    <Text style={styles.joinDate}>
                      Joined: {new Date(user.date_joined).toLocaleDateString()}
                    </Text>
                  </View>
                  <View style={styles.userActions}>
                    <TouchableOpacity
                      style={[styles.actionBtn, styles.unblockBtn]}
                      onPress={() => unblockUser(user.id)}
                    >
                      <Ionicons name="checkmark-circle-outline" size={16} color="#fff" />
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={[styles.actionBtn, styles.deleteBtn]}
                      onPress={() => deleteUser(user.id)}
                    >
                      <Ionicons name="trash-outline" size={16} color="#fff" />
                    </TouchableOpacity>
                  </View>
                </View>
              ))}
            </ScrollView>
          </>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
  },
  header: {
    backgroundColor: "#d40000",
    padding: 20,
    paddingTop: 50,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#fff",
    flex: 1,
    textAlign: "center",
  },
  placeholder: {
    width: 40,
  },
  content: {
    flex: 1,
    padding: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  loadingText: {
    fontSize: 16,
    color: "#666",
  },
  emptyContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  emptyText: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#666",
    marginTop: 20,
  },
  emptySubtext: {
    fontSize: 14,
    color: "#999",
    marginTop: 8,
  },
  statsHeader: {
    backgroundColor: "#fff",
    padding: 15,
    borderRadius: 10,
    marginBottom: 20,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statsText: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#d40000",
    textAlign: "center",
  },
  usersList: {
    flex: 1,
  },
  userCard: {
    backgroundColor: "#fff",
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
    borderLeftWidth: 4,
    borderLeftColor: "#f44336",
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#333",
  },
  userEmail: {
    fontSize: 14,
    color: "#666",
    marginTop: 2,
  },
  userStatus: {
    flexDirection: "row",
    marginTop: 8,
    gap: 8,
  },
  statusBadge: {
    fontSize: 10,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
    color: "#fff",
    fontWeight: "bold",
  },
  blockedBadge: {
    fontSize: 10,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
    backgroundColor: "#f44336",
    color: "#fff",
    fontWeight: "bold",
  },
  verifiedBadge: {
    backgroundColor: "#2196F3",
  },
  unverifiedBadge: {
    backgroundColor: "#FF9800",
  },
  joinDate: {
    fontSize: 12,
    color: "#999",
    marginTop: 4,
  },
  userActions: {
    flexDirection: "row",
    gap: 8,
  },
  actionBtn: {
    padding: 8,
    borderRadius: 6,
  },
  unblockBtn: {
    backgroundColor: "#4CAF50",
  },
  deleteBtn: {
    backgroundColor: "#f44336",
  },
});