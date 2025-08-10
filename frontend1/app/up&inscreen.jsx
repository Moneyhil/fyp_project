import { View, Text, StyleSheet, Image, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router'; 

export default function mainscreen(){
    const router = useRouter();
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Blood Donation App</Text>

      <Image
        source={require('../assets/images/mres.png')} 
        style={styles.image}
      />

      <Text style={styles.text}>Donate Blood, Save lives!!</Text>

      <TouchableOpacity style={styles.signupbutton} onPress={() => router.push('/signup')}>
        <Text style={styles.buttontext}>Sign Up</Text>
      </TouchableOpacity>

      <Text style={styles.accounttext}>Already have account.!</Text>

      <TouchableOpacity style={styles.loginbutton} onPress={() => router.push('/signin')}>
        <Text style={styles.buttontext}>Log In</Text>
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
    resizeMode: 'contain',
    marginBottom: 20,
  },
  text: {
    fontSize: 20,
    color: '#291b1b',
    marginBottom: 15,
    fontWeight: '600',
  },
  signupbutton: {
    backgroundColor: '#d40000',
    paddingHorizontal:100,
    paddingVertical: 12,
    borderRadius: 25,
    marginTop: 20,
    marginBottom: 10,
    alignItems: 'center',
    shadowColor: '#d40000',
    shadowOpacity: 0.3,
    shadowOffset: { width: 0, height: 3 },
    shadowRadius: 6,
  },
  loginbutton: {
     backgroundColor: '#d40000',
    paddingVertical: 12,
    paddingHorizontal:100,
    borderRadius: 25,
    marginTop: 20,
    marginBottom: 10,
    alignItems: 'center',
    shadowColor: '#d40000',
    shadowOpacity: 0.3,
    shadowOffset: { width: 0, height: 3 },
    shadowRadius: 6,
  },
  buttontext: {
    color: '#fff9f8ff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  accounttext: {
    fontSize: 12,
    color: '#777',
    marginBottom: 5,
  },
});
