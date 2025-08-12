import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import axios from 'axios';
import * as Yup from 'yup';

export default function Registration() {
  const router = useRouter();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmpassword: '',
  });

  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [loading, setLoading] = useState(false);
  const API_BASE_URL = "http://192.168.100.16:8000"; 

  const validationSchema = Yup.object().shape({
    name: Yup.string()
    .max(50, 'Name must be at most 50 characters').required('Name is required'),
    email: Yup.string().email('Invalid email format').required('Email is required'),
    password: Yup.string()
    .required('Password is required')
    .min(8, 'Password must be at least 8 characters')
    .matches(/[a-zA-Z]/, 'Password must contain at least one letter')
    .matches(/\d/, 'Password must contain at least one number'),
    confirmpassword: Yup.string()
      .oneOf([Yup.ref('password'), null], 'Passwords must match')
      .required('Confirm password is required'),
  });

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (touched[field]) {
      validationSchema
        .validateAt(field, { ...formData, [field]: value })
        .then(() => setErrors(prev => ({ ...prev, [field]: '' })))
        .catch(err => setErrors(prev => ({ ...prev, [field]: err.message })));
    }
  };

  const handleBlur = (field) => {
    setTouched(prev => ({ ...prev, [field]: true }));
  };

  const getInputStyle = (field) => {
    return touched[field] && errors[field] ? [styles.input, styles.inputError] : styles.input;
  };

  const handleSignup = async () => {
    setTouched({
      name: true,
      email: true,
      password: true,
      confirmpassword: true,
    });

    setLoading(true);

    try {
      await validationSchema.validate(formData, { abortEarly: false });
      setErrors({});

      const payload = {
        name: formData.name,
        email: formData.email,
        password: formData.password,
        confirmpassword: formData.confirmpassword,
      };

      const response = await axios.post(
        `${API_BASE_URL}/donation/send-otp/`,
        payload,
        {
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
        }
      );

      if (response.status === 201) {
        Alert.alert("Success", "OTP sent to your email!");
        router.push({ pathname: "/otp", params: { email: formData.email } });
      }
    } catch (err) {
      if (err.response) {
        Alert.alert("Error", err.response.data?.error || "Registration failed");
      } else if (err.name === "ValidationError") {
        const formErrors = {};
        err.inner.forEach((e) => formErrors[e.path] = e.message);
        setErrors(formErrors);
      } else {
        Alert.alert("Error", "Network error. Try again.");
      }
    } finally {
      setLoading(false);
    }
  };



  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View>
        <Text style={styles.heading}>Sign Up</Text>

        <Text style={styles.label}>Full Name</Text>
        <TextInput
          placeholder="Enter your full name"
          value={formData.name}
          onChangeText={text => handleChange('name', text)}
          onBlur={() => handleBlur('name')}
          style={getInputStyle('name')}
        />
        {touched.name && errors.name && <Text style={styles.errorText}>{errors.name}</Text>}

        <Text style={styles.label}>Email Address</Text>
        <TextInput
          placeholder="Enter your email"
          value={formData.email}
          onChangeText={text => handleChange('email', text)}
          onBlur={() => handleBlur('email')}
          style={getInputStyle('email')}
          keyboardType="email-address"
          autoCapitalize="none"
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

        <Text style={styles.label}>Confirm Password</Text>
        <TextInput
          placeholder="********"
          value={formData.confirmpassword}
          onChangeText={text => handleChange('confirmpassword', text)}
          onBlur={() => handleBlur('confirmpassword')}
          style={getInputStyle('confirmpassword')}
          secureTextEntry
        />
        {touched.confirmpassword && errors.confirmpassword && <Text style={styles.errorText}>{errors.confirmpassword}</Text>}

        <TouchableOpacity style={styles.button} onPress={handleSignup} disabled={loading}>
          <Text style={styles.buttonText}>{loading ? 'Processing...' : 'Sign Up'}</Text>
        </TouchableOpacity>

        <Text style={styles.text}>
          Already have an account?{' '}
          <Text style={styles.Link} onPress={() => router.push('/signin')}>
            Log In
          </Text>
        </Text>
      </View>
    </ScrollView>
  );
}

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
