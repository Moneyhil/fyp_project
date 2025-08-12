import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import * as Yup from 'yup';

export default function Login() {
  const router = useRouter();

  // Form state
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  // Validation error state
  const [errors, setErrors] = useState({});
  // Track touched fields
  const [touched, setTouched] = useState({});

  // Validation schema (Yup)
  const validationSchema = Yup.object().shape({
    email: Yup.string()
      .email('Invalid email format')
      .required('Email is required'),
    password: Yup.string()
      .required('Password is required')
      .min(8, 'Password must be at least 8 characters'),
  });

  // Handle input change
  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));

    // Validate field if touched
    if (touched[field]) {
      validationSchema
        .validateAt(field, { ...formData, [field]: value })
        .then(() => setErrors(prev => ({ ...prev, [field]: '' })))
        .catch(err => setErrors(prev => ({ ...prev, [field]: err.message })));
    }
  };

  // Mark field as touched
  const handleBlur = (field) => {
    setTouched(prev => ({ ...prev, [field]: true }));
  };

  // Dynamic input style for errors
  const getInputStyle = (field) => {
    return touched[field] && errors[field] ? [styles.input, styles.inputError] : styles.input;
  };

  // Handle login submission (validation only)
  const handleLogin = async () => {
    // Mark all fields as touched to show errors
    setTouched({
      email: true,
      password: true,
    });

    try {
      // Validate entire form
      await validationSchema.validate(formData, { abortEarly: false });
      setErrors({}); // Clear errors if valid
      
      Alert.alert('Success', 'Form is valid!');
      // Here you would normally call your API
       router.push('/home'); 
      
    } catch (err) {
      if (err.name === 'ValidationError') {
        // Yup validation errors
        const formErrors = {};
        err.inner.forEach(e => {
          formErrors[e.path] = e.message;
        });
        setErrors(formErrors);
      } else {
        Alert.alert('Error', 'Something went wrong during validation');
      }
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View>
        <Text style={styles.heading}>Log In</Text>

        <Text style={styles.label}>Email Address</Text>
        <TextInput
          placeholder="Enter your email"
          value={formData.email}
          onChangeText={text => handleChange('email', text)}
          onBlur={() => handleBlur('email')}
          style={getInputStyle('email')}
          keyboardType="email-address"
        />
        {touched.email && errors.email && <Text style={styles.errorText}>{errors.email}</Text>}

        <Text style={styles.label}>Password</Text>
        <TextInput
          placeholder="********"
          value={formData.password}
          onChangeText={text => handleChange('password', text)}
          onBlur={() => handleBlur('password')}
          style={getInputStyle('password')}
          secureTextEntry
        />
        {touched.password && errors.password && <Text style={styles.errorText}>{errors.password}</Text>}

        <TouchableOpacity style={styles.button} onPress={handleLogin}>
          <Text style={styles.buttonText}>Log In</Text>
        </TouchableOpacity>

        <Text style={styles.text}>
          Don't have an account?{' '}
          <Text style={styles.Link} onPress={() => router.push('/signup')}>
            Sign Up
          </Text>
        </Text>
      </View>
    </ScrollView>
  );
}

// Reuse the same styles from your registration component
const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
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
    fontSize: 14,
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