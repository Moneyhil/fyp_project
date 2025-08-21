import React, { useEffect } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import Svg, { Path, Circle } from 'react-native-svg';

const BloodDropLogo = () => (
  <Svg width="150" height="150" viewBox="0 0 150 150">
    {/* Blood drop shape */}
    <Path
      d="M75 20 C85 30, 110 55, 110 85 C110 110, 95 125, 75 125 C55 125, 40 110, 40 85 C40 55, 65 30, 75 20 Z"
      fill="#E53E3E"
      stroke="#C53030"
      strokeWidth="2"
    />
    {/* Heart symbol inside */}
    <Path
      d="M75 65 C70 55, 55 55, 55 70 C55 80, 75 95, 75 95 C75 95, 95 80, 95 70 C95 55, 80 55, 75 65 Z"
      fill="#FFFFFF"
    />
    {/* Plus sign for medical symbol */}
    <Path
      d="M72 45 L78 45 L78 55 L88 55 L88 61 L78 61 L78 71 L72 71 L72 61 L62 61 L62 55 L72 55 Z"
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
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        tension: 50,
        friction: 7,
        useNativeDriver: true,
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
        <Animated.View style={[styles.logo, { opacity: fadeAnim }]}>
          <BloodDropLogo />
        </Animated.View>
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
    color: '#E53E3E', // Red text color
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
    marginBottom: 40,
    fontStyle: 'italic',
  },

});