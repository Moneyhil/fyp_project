import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet,} from 'react-native';
import { router } from 'expo-router';


export default function LoginScreen() {
    const [form, setForm] = useState({ email: '', password: '' });
     const handleChange = (name, value) => {
    setForm(prevForm => ({ ...prevForm, [name]: value }));
  };
const handleLogin = () => {
    // ✅ Here you can add authentication logic.
    // If successful, navigate to home or dashboard screen (e.g., 'home')
    router.push('/home'); // Make sure /app/home.jsx exists
  };

  return (
 
      <View style={styles.container}>
        <Text style={styles.heading}>Log In</Text>

        <Text style={styles.label}>Email Address</Text>
        <TextInput
          placeholder="Enter your Email"
          value={form.email}
          onChangeText={text => handleChange("email", text)}
          style={styles.input}
          keyboardType="email-address"
        />
         <Text style={styles.label}>Password</Text>
        <TextInput
          placeholder="Enter password"
          value={form.password}
          onChangeText={text => handleChange("password", text)}
          style={styles.input}
          secureTextEntry
        />


        <View style={styles.forgot}>
         <Text style={styles.text}>
          Forget your password?{' '}
          <Text
            style={styles.Link}
            onPress={() => router.push('forgetpassword')}>
            Forget password
          </Text>
        </Text>
        </View>

        <TouchableOpacity style={styles.button} onPress={handleLogin}>
          <Text style={styles.buttonText}>Log In</Text>
        </TouchableOpacity>
      </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    justifyContent: 'center',
    padding: 25,
  },
  heading: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#cc0000',
    marginBottom: 20,
    textAlign: 'center',
  },
  label: {
    fontWeight: 'bold',
    marginTop: 10,
    marginBottom: 5,
    color: '#333',
  },
  input: {
    width: '100%',
    borderRadius: 8,
    paddingHorizontal: 15,
    paddingVertical: 10,
    fontSize: 12,
    marginBottom: 5,
    backgroundColor: '#f2f2f2',
  },
  forgot: {
    flexDirection: 'row',
    alignSelf: 'flex-start',
    marginTop: 5,
    marginBottom: 20,
  },
  Link: {
    color: 'blue',
    textDecorationLine: 'underline',
  },
  button: {
    backgroundColor: '#d40000',
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
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
});
