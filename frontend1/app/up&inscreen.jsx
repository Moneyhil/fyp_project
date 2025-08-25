import { View, Text, StyleSheet, Image, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function mainscreen(){
    const router = useRouter();
    const [isCheckingAuth, setIsCheckingAuth] = useState(true);

    useEffect(() => {
        checkAuthAndRedirect();
    }, []);

    const checkAuthAndRedirect = async () => {
        try {
            const authToken = await AsyncStorage.getItem('authToken');
            const userInfo = await AsyncStorage.getItem('userInfo');
            
            if (authToken && userInfo) {
                const user = JSON.parse(userInfo);
                if (user.is_staff) {
                    router.replace('/admindashboard');
                } else {
                    router.replace('/home');
                }
                return;
            }
        } catch (error) {
            console.error('Auth check error:', error);
        } finally {
            setIsCheckingAuth(false);
        }
    };

    if (isCheckingAuth) {
        return null; 
    }
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Blood Donation App</Text>

      <Image
        source={require('../assets/images/mres.png')} 
        style={styles.image}
        resizeMode="contain"
      />

      <Text style={styles.text}>Donate Blood, Save lives!!</Text>

      <TouchableOpacity style={styles.button} onPress={() => router.push('/signup')}>
        <Text style={styles.buttontext}>Sign Up</Text>
      </TouchableOpacity>

      <Text style={styles.accounttext}>Already have an account??</Text>

      <TouchableOpacity style={styles.button} onPress={() => router.push('/signin')}>
        <Text style={styles.buttontext}>Sign In</Text>
      </TouchableOpacity>

      <Text style={styles.accounttext}>Only Admins can sign in...</Text>

      <TouchableOpacity style={styles.adminbutton} onPress={() => router.push('/adminsignin')}>
        <Text style={styles.buttontext}>Admin Sign In</Text>
      </TouchableOpacity>
    </View>
  );
}
const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 80,
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 30,
    fontWeight: 'bold',
    color: '#1f1717ff',
    marginBottom: 20,
  },
  image: {
    width: 250,
    height: 250,
    marginBottom: 20,
  },
  text: {
    fontSize: 20,
    color: '#291b1b',
    marginBottom: 15,
    fontWeight: '600',
  },
  button: {
    backgroundColor: '#d40000',
    paddingHorizontal:100,
    paddingVertical: 12,
    borderRadius: 25,
    marginTop: 20,
    marginBottom: 10,
    alignItems: 'center',
    shadowColor: '#d40000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 1,
    shadowRadius: 6,
    elevation: 5,
  },
  adminbutton: {
    backgroundColor: '#d40000',
    paddingHorizontal:70,
    paddingVertical: 12,
    borderRadius: 25,
    marginTop: 10,
    marginBottom: 20,
    alignItems: 'center',
    shadowColor: '#d40000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 1,
    shadowRadius: 6,
    elevation: 5
  },
  buttontext: {
    color: '#fff9f8ff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  accounttext: {
    fontSize: 12,
    color: '#777',
    marginBottom: 2,
    marginTop: 10,
  },
});
