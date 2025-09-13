import { Stack } from "expo-router";
import { useState, useEffect } from 'react';
import SplashScreen from './SplashScreen';

export default function RootLayout() {
  const [showSplash, setShowSplash] = useState(true);

  useEffect(() => {
    
    const timer = setTimeout(() => {
      setShowSplash(false);
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  if (showSplash) {
    return <SplashScreen />;
  }

  return <Stack screenOptions={{headerShown : false,}} />;
}
