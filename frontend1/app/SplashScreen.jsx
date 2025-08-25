import React, { useEffect } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import Svg, { Path } from 'react-native-svg';

const BloodDropLogo = () => (
  <Svg width="150" height="150" viewBox="0 0 150 150">
    {/* Simple blood drop shape */}
    <Path
      d="M75 20 C85 30, 110 55, 110 85 C110 110, 95 125, 75 125 C55 125, 40 110, 40 85 C40 55, 65 30, 75 20 Z"
      fill="#E53E3E"
    />
  </Svg>
);

export default function SplashScreen() {
  const fadeAnim = new Animated.Value(0);
  const scaleAnim = new Animated.Value(0.8);

  useEffect(() => {
    // Start animations
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 1000,
        useNativeDriver: false, // Changed from true to false
      }),
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration: 1000,
        useNativeDriver: false, // Changed from true to false
      }),
    ]).start();
  }, []);

  return (
    <View style={styles.container}>
      <Animated.View 
        style={[
          styles.content,
          {
            opacity: fadeAnim,
            transform: [{ scale: scaleAnim }]
          }
        ]}
      >
        <View style={styles.logo}>
          <BloodDropLogo />
        </View>
        <Text style={styles.appName}>Blood Donation App</Text>
        <Text style={styles.tagline}>Saving Lives, One Drop at a Time</Text>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF', // Clean white background
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  logo: {
    width: 150,
    height: 150,
    marginBottom: 20,
  },
  appName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#d40000', // Red text color
    textAlign: 'center',
    marginBottom: 10,
    textShadowColor: 'rgba(229, 62, 62, 0.2)',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 3,
  },
  tagline: {
    fontSize: 16,
    color: '#718096', // Gray text for tagline
    textAlign: 'center',
    fontStyle: 'italic',
  },

});