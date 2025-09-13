import React from 'react';
import { View, Text, StyleSheet, ScrollView, Image, TouchableOpacity } from 'react-native';
import { router } from 'expo-router';

export default function AboutScreen() {
  return (
    <View style={styles.container}>

      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton} 
          onPress={() => router.back()}
        >
          <Text style={styles.backButtonText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerText}>About</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        
        <View style={styles.content}>
          
          <View style={styles.imageContainer}>
            <Image 
              source={require('../assets/images/drop.png')} 
              style={styles.appImage}
              resizeMode="contain"
            />
          </View>

          
          <View style={styles.infoContainer}>
            <Text style={styles.appTitle}>Blood Donation App</Text>
            <Text style={styles.version}>Version 1.0.0</Text>
            
            <Text style={styles.description}>
              Our Blood Donation App connects blood donors with those in need, 
              making it easier to save lives through voluntary blood donation. 
              Join our community of heroes who help save lives every day.
            </Text>

            <View style={styles.featuresContainer}>
              <Text style={styles.featuresTitle}>Key Features:</Text>
              <Text style={styles.featureItem}>• Easy donor registration</Text>
              <Text style={styles.featureItem}>• Find blood donors nearby</Text>
              <Text style={styles.featureItem}>• Secure user profiles</Text>
              <Text style={styles.featureItem}>• Real-time notifications</Text>
              <Text style={styles.featureItem}>• Emergency blood requests</Text>
            </View>

          </View>
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
  header: {
    backgroundColor: '#d40000',
    width: '100%',
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
  backButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  headerText: {
    color: '#fff',
    fontSize: 22,
    fontWeight: 'bold',
  },
  placeholder: {
    width: 50, 
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingBottom: 20,
  },
  content: {
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  imageContainer: {
    marginBottom: 20,
    alignItems: 'center',
  },
  appImage: {
    width: 120,
    height: 80,
  },
  infoContainer: {
    width: '100%',
    alignItems: 'center',
  },
  appTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#d40000',
    marginBottom: 5,
    textAlign: 'center',
  },
  version: {
    fontSize: 16,
    color: '#666',
    marginBottom: 20,
  },
  description: {
    fontSize: 16,
    color: '#333',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 30,
    paddingHorizontal: 20,
  },
  featuresContainer: {
    width: '100%',
    marginBottom: 20,
    paddingHorizontal: 20,
  },
  featuresTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#d40000',
    marginBottom: 15,
    textAlign: 'center',
  },
  featureItem: {
    fontSize: 16,
    color: '#333',
    marginBottom: 8,
    paddingLeft: 20,
  },
});