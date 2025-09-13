import React, { useState, useEffect } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Alert } from "react-native";
import { useRouter } from "expo-router";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Ionicons } from "@expo/vector-icons";
import api from "../constants/API";

export default function AdminDashboard() {
  const router = useRouter();
  const [adminInfo, setAdminInfo] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAdminAuth();
    loadUsers();
  }, []);

  const checkAdminAuth = async () => {
    try {
      const userInfo = await AsyncStorage.getItem("userInfo");
      const token = await AsyncStorage.getItem("authToken");
      
      if (!userInfo || !token) {
        Alert.alert("Error", "Please login again");
        router.replace("/signin");
        return;
      }

      const user = JSON.parse(userInfo);
      if (!user.is_staff) {
        Alert.alert("Access Denied", "You don't have admin privileges");
        router.replace("/signin");
        return;
      }

      setAdminInfo(user);
    } catch (error) {
      console.error("Auth check error:", error);
      router.replace("/signin");
    }
  };

  const loadUsers = async () => {
    try {
      const token = await AsyncStorage.getItem("authToken");
      const response = await api.get("/donation/admin/users/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.status === 200) {
        setUsers(response.data.users || []);
      }
    } catch (error) {
      console.error("Load users error:", error);
      Alert.alert("Error", "Failed to load users");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    Alert.alert(
      "Logout",
      "Are you sure you want to logout?",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Logout",
          onPress: async () => {
            try {
          
              const authToken = await AsyncStorage.getItem("authToken");
              const refreshToken = await AsyncStorage.getItem("refreshToken");
              
            
              if (authToken && refreshToken) {
                try {
                  await api.post(
                    '/donation/admin-logout/',
                    { refresh_token: refreshToken },
                    {
                      headers: {
                        'Authorization': `Bearer ${authToken}`,
                        'Content-Type': 'application/json'
                      }
                    }
                  );
                } catch (apiError) {
                  console.log('Admin logout API error:', apiError);
          
                }
              }
              
        
              await AsyncStorage.multiRemove(["authToken", "refreshToken", "userInfo"]);
              
              Alert.alert('Success', 'Logged out successfully!', [
                {
                  text: 'OK',
                  onPress: () => router.replace("/signin")
                }
              ]);
            } catch (error) {
              console.error("Logout error:", error);
      
              await AsyncStorage.multiRemove(["authToken", "refreshToken", "userInfo"]);
              router.replace("/signin");
            }
          },
        },
      ]
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
  
      <View style={styles.header}>
        <View>
          <Text style={styles.welcomeText}>Welcome, Admin</Text>
          <Text style={styles.emailText}>{adminInfo?.email}</Text>
        </View>
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Ionicons name="log-out-outline" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

    
      <View style={styles.statsContainer}>
        <TouchableOpacity 
          style={styles.blockedProfilesCard}
          onPress={() => router.push("/blockedprofiles")}
        >
          <Ionicons name="ban-outline" size={32} color="#fff" />
          <Text style={styles.blockedProfilesNumber}>{users.filter(u => !u.is_active).length}</Text>
          <Text style={styles.blockedProfilesLabel}>Blocked Profiles</Text>
        </TouchableOpacity>
      </View>


    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#f5f5f5",
  },
  loadingText: {
    fontSize: 16,
    color: "#666",
  },
  header: {
    backgroundColor: "#d40000",
    padding: 20,
    paddingTop: 50,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  welcomeText: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#fff",
  },
  emailText: {
    fontSize: 14,
    color: "#fff",
    opacity: 0.8,
  },
  logoutButton: {
    padding: 8,
  },
  statsContainer: {
    padding: 20,
    alignItems: "center",
  },
  blockedProfilesCard: {
    backgroundColor: "#d40000",
    padding: 20,
    borderRadius: 15,
    alignItems: "center",
    justifyContent: "center",
    width: "80%",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 6,
    elevation: 5,
  },
  blockedProfilesNumber: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#fff",
    marginTop: 8,
  },
  blockedProfilesLabel: {
    fontSize: 14,
    color: "#fff",
    marginTop: 5,
    fontWeight: "600",
  },

});