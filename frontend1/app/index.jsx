import { View, Text, Image, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import { checkAuthStatus, redirectBasedOnRole } from '../utils/authUtils';

export default function index() {
  const router = useRouter();
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  useEffect(() => {
    checkAuthAndRedirect();
  }, []);

  const checkAuthAndRedirect = async () => {
    try {
      const { isAuthenticated, user } = await checkAuthStatus();
      
      if (isAuthenticated && user) {
        redirectBasedOnRole(user, router);
        return;
      }
    } catch (error) {
      console.error('Auth check error:', error);
    } finally {
      setIsCheckingAuth(false);
    }
  };

  if (isCheckingAuth) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#d40000" />
        <Text style={styles.loadingText}>Checking login session...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.qoutecard}>
        <Text style={styles.qoutetext}>Every Drop of Blood you Donate is a Silent Promise of Hope, a Powerful act of love and a Lifeline for some one in Need."</Text>
      </View>
      <Text style={styles.appname}>Welcome</Text>
      <Image
        source={require('../assets/images/mandw.png')} 
        style={styles.image}
        resizeMode="contain" />
      <View style={styles.card}>
        <Text style={styles.textcard}>"Because Someone, Somewhere, is Counting on You."</Text>
       
       <TouchableOpacity
        style={styles.button}
        onPress={() => router.push('/upinscreen')}>
        <Text style={styles.buttonLabel}>Donate</Text>
      </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  qoutecard:{
    backgroundColor: '#f7d0d0ff',
    padding: 20,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#e46565ff',
    marginBottom: 20,
    shadowColor: '#f33535',
    shadowOffset: {
      width: 0,
      height: 3,
    },
    shadowOpacity: 1,
    shadowRadius: 6,
    elevation: 5,
    width: '90%',
  },
  qoutetext:{
    fontSize: 16,
    fontStyle: 'italic',
    color: '#333',
    textAlign: 'center',
  },
  container: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  appname: {
    alignItems: "center",
    fontSize: 35,
    fontWeight: 'bold',
  },
  image: {
    marginTop:0,
    width: 300,
    height: 300,
  },
  card:{
    backgroundColor: '#f7d0d0ff',
    padding: 20,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#e46565ff',
    marginBottom: 20,
    shadowColor: '#d40000',
    shadowOffset: {
      width: 0,
      height: 3,
    },
    shadowOpacity: 1,
    shadowRadius: 6,
    elevation: 5,
    width: '90%',
  },
  textcard:{
    fontSize: 16,
    fontWeight: '600',
    fontStyle: 'italic',
    color: '#333',
    textAlign: 'center',
  },
  button:{
    backgroundColor: '#64cbfaff',  
    paddingVertical: 12,
    paddingHorizontal: 25,
    borderRadius: 25,
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 10,
    shadowColor: '#457acaff',
    shadowOffset: {
      width: 0,
      height: 3,
    },
    shadowOpacity: 1,
    shadowRadius: 6,
    elevation: 5,
  },
  buttonLabel:{
    color: '#0e0b0aff',
    fontWeight:'700'
  },

})

