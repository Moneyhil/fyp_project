import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import axios from 'axios';
import * as Yup from 'yup';

export default function Signup1() {
  const router = useRouter();

  const [formData, setFormData] = useState({
    first_name: '',
    email: '',
    phone_number: '',
    password: '',
    confirmpassword: ''
  });
  const [errors, setErrors] = useState({
    first_name: '',
    email: '',
    phone_number: '',
    password: '',
    confirmpassword: ''
  });
  const [touched, setTouched] = useState({
    first_name: false,
    email: false,
    phone_number: false,
    password: false,
    confirmpassword: false
  });

  const validationSchema = Yup.object().shape({
    first_name: Yup.string()
      .max(50, 'First name must be at most 50 characters')
      .required('First name is required'),

    email: Yup.string()
      .email('Invalid email format')
      .required('Email is required'),

    phone_number: Yup.string()
      .matches(/^\d{11}$/, 'Phone number must be exactly 11 digits')
      .required('Phone number is required'),

    password: Yup.string()
      .required('Password is required')
      .min(8, 'Password must be at least 8 characters')
      .matches(/[a-zA-Z]/, 'Password must contain at least one letter')
      .matches(/[^a-zA-Z0-9]/, 'Password must contain at least one special character'),

    confirmpassword: Yup.string()
      .oneOf([Yup.ref('password'), null], 'Passwords must match')
      .required('Confirm password is required'),
  });

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Validate the field when it's changed and has been touched
    if (touched[field]) {
      validationSchema.validateAt(field, { [field]: value })
        .then(() => setErrors(prev => ({ ...prev, [field]: '' })))
        .catch(err => setErrors(prev => ({ ...prev, [field]: err.message })));
    }
  };

  const handleSignup1 = async () => {
    try {
      // Mark all fields as touched to show all errors
      setTouched({
        first_name: true,
        email: true,
        phone_number: true,
        password: true,
        confirmpassword: true
      });

      // Validate the entire form
      await validationSchema.validate(formData, { abortEarly: false });

      // Check if backend is reachable
      try {
        const ping = await fetch('http://192.168.100.16:8000/signup1/', { method: 'OPTIONS' });
        console.log('Backend reachable:', ping.status);
      } catch (pingErr) {
        console.error('Backend not reachable:', pingErr);
        Alert.alert('Error', 'Cannot connect to server. Check network.');
        return;
      }

      const response = await axios.post('http://192.168.100.16:8000/signup1/', formData);

      console.log('Response:', response);

      if (response.status === 201) {
        Alert.alert('Signup successful', 'You can now log in.');
        router.push('/otp');
      } else {
        Alert.alert('Signup failed', response.data.message || 'Unknown error');
      }
    } catch (err) {
      console.log('Error in signup:', err);

      if (err.name === 'ValidationError') {
        // Update all error messages
        const newErrors = {};
        err.inner.forEach(error => {
          newErrors[error.path] = error.message;
        });
        setErrors(newErrors);
      } else if (err.response) {
        Alert.alert('Signup Failed', err.response.data.message || 'Server error');
      } else {
        Alert.alert('Error', 'Could not connect to server.');
      }
    }
  };

  // Helper function to determine input style based on error state
  const getInputStyle = (field) => {
    if (touched[field] && errors[field]) {
      return [styles.input, styles.inputError];
    }
    return styles.input;
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View>
        <Text style={styles.heading}>Sign Up</Text>

        <Text style={styles.label}>Full Name</Text>
        <TextInput
          placeholder="Enter your full name"
          value={formData.first_name}
          onChangeText={(text) => handleChange('first_name', text)}
          style={getInputStyle('first_name')}
        />
        {touched.first_name && errors.first_name && (
          <Text style={styles.errorText}>{errors.first_name}</Text>
        )}

        <Text style={styles.label}>Email Address</Text>
        <TextInput
          placeholder="Enter your Email"
          value={formData.email}
          onChangeText={(text) => handleChange('email', text)}

          style={getInputStyle('email')}
          keyboardType="email-address"
          autoCapitalize="none"
        />
        {touched.email && errors.email && (
          <Text style={styles.errorText}>{errors.email}</Text>
        )}

        <Text style={styles.label}>Phone number</Text>
        <TextInput
          placeholder="Enter your phone number"
          value={formData.phone_number}
          onChangeText={(text) => handleChange('phone_number', text)}
          style={getInputStyle('phone_number')}
          keyboardType="phone-pad"
        />
        {touched.phone_number && errors.phone_number && (
          <Text style={styles.errorText}>{errors.phone_number}</Text>
        )}

        <Text style={styles.label}>Password</Text>
        <TextInput
          placeholder="Enter password (min 8 chars with letters & special chars)"
          value={formData.password}
          onChangeText={(text) => handleChange('password', text)}
          style={getInputStyle('password')}
          secureTextEntry
        />
        {touched.password && errors.password && (
          <Text style={styles.errorText}>{errors.password}</Text>
        )}

        <Text style={styles.label}>Confirm Password</Text>
        <TextInput
          placeholder="Confirm your password"
          value={formData.confirmpassword}
          onChangeText={(text) => handleChange('confirmpassword', text)}
          style={getInputStyle('confirmpassword')}
          secureTextEntry
        />
        {touched.confirmpassword && errors.confirmpassword && (
          <Text style={styles.errorText}>{errors.confirmpassword}</Text>
        )}

        <TouchableOpacity style={styles.button} onPress={handleSignup1}>
          <Text style={styles.buttonText}>Sign Up</Text>
        </TouchableOpacity>

        <Text style={styles.text}>
          Already have an account?{' '}
          <Text style={styles.Link} onPress={() => router.push('signin')}>
            Log In
          </Text>
        </Text>
      </View>
    </ScrollView>
  );
}

export const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 25,
    backgroundColor: '#fff',
  },
  heading: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#c00808ff',
    textAlign: 'center',
    marginBottom: 20,
  },
  label: {
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
    marginTop: 10,
  },
  input: {
    backgroundColor: '#f2f2f2',
    borderRadius: 8,
    paddingHorizontal: 15,
    paddingVertical: 10,
    fontSize: 12,
    marginBottom: 5,
    borderWidth: 1,
    borderColor: '#f2f2f2',
  },
  inputError: {
    borderColor: '#ff0000',
  },
  errorText: {
    color: '#ff0000',
    fontSize: 12,
    marginBottom: 5,
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
  text: {
    textAlign: 'center',
    color: '#444',
    marginTop: 10,
  },
  Link: {
    color: '#0000ff',
    textDecorationLine: 'underline',
  },
});