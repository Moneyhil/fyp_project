import React, { useState, useEffect } from "react";
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ScrollView, KeyboardAvoidingView, Platform } from "react-native";
import { useRouter } from "expo-router";
import * as Yup from "yup";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Ionicons } from "@expo/vector-icons";
import api from "../constants/API";
import { checkAuthStatus, saveAuthData } from '../utils/authUtils';

export default function Login() {
  const router = useRouter();
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);


  useEffect(() => {
    checkAuthAndRedirect();
  }, []);

  
  const checkAuthAndRedirect = async () => {
    try {
      const { isAuthenticated, user } = await checkAuthStatus();
      
      if (isAuthenticated && user) {
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

  // Validation schema
  const validationSchema = Yup.object().shape({
    email: Yup.string().email("Invalid email format").required("Email is required"),
    password: Yup.string().required("Password is required"),
  });

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (touched[field]) {
      validationSchema
        .validateAt(field, { ...formData, [field]: value })
        .then(() => setErrors((prev) => ({ ...prev, [field]: "" })))
        .catch((err) => setErrors((prev) => ({ ...prev, [field]: err.message })));
    }
  };

  const handleBlur = (field) => {
    setTouched((prev) => ({ ...prev, [field]: true }));
  };

  const getInputStyle = (field) => {
    return touched[field] && errors[field] ? [styles.input, styles.inputError] : styles.input;
  };

  const handleLogin = async () => {
    setTouched({ email: true, password: true });
    setLoading(true);

    try {
      await validationSchema.validate(formData, { abortEarly: false });
      setErrors({});

      const response = await api.post(
        "/donation/login/",
        {
          email: formData.email,
          password: formData.password,
        }
      );

      console.log('Login response:', response.data); 

      if (response.status === 200) {
        const { token, access_token, refresh_token, user } = response.data;
        
        
        const authToken = token || access_token;
        
        console.log('Auth token:', authToken); 
        console.log('Refresh token:', refresh_token); 
        
        if (authToken && refresh_token && user) {
          
          await AsyncStorage.setItem('authToken', authToken);
          await AsyncStorage.setItem('refreshToken', refresh_token);
          await AsyncStorage.setItem('userInfo', JSON.stringify(user));
        }
        console.log('User:', user); 

        if (!authToken) {
          Alert.alert("Error", "No authentication token received");
          return;
        }

        
        await AsyncStorage.setItem('authToken', authToken);
        await AsyncStorage.setItem('refreshToken', refresh_token);
        await AsyncStorage.setItem('userInfo', JSON.stringify(user));
        
        Alert.alert("Success", "Login successful!");
        
      
        if (user.is_staff) {
          router.replace('/admindashboard');
        } else {
          router.replace('/home');
        }
      }
    } catch (err) {
      if (err.response) {
        
        if (err.response.status === 400 && err.response.data) {
          const errorData = err.response.data;
          if (typeof errorData === 'object' && !errorData.error) {
          
            const formErrors = {};
            Object.keys(errorData).forEach(field => {
              if (Array.isArray(errorData[field])) {
                formErrors[field] = errorData[field][0];
              } else {
                formErrors[field] = errorData[field];
              }
            });
            setErrors(formErrors);
          } else {
            Alert.alert("Error", errorData.error || errorData.non_field_errors?.[0] || "Invalid email or password");
          }
        } else {
          Alert.alert("Error", err.response.data?.error || "Invalid email or password");
        }
      } else if (err.name === "ValidationError") {
        const formErrors = {};
        err.inner.forEach((e) => (formErrors[e.path] = e.message));
        setErrors(formErrors);
      } else {
        Alert.alert("Error", "Network error. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      style={{ flex: 1 }} 
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      keyboardVerticalOffset={Platform.OS === "ios" ? 64 : 0}
    >
      <ScrollView contentContainerStyle={styles.container}>
        <View>
          <Text style={styles.heading}>Log In</Text>

        <Text style={styles.label}>Email Address</Text>
        <TextInput
          placeholder="Enter your email"
          value={formData.email}
          onChangeText={(text) => handleChange("email", text)}
          onBlur={() => handleBlur("email")}
          style={getInputStyle("email")}
          keyboardType="email-address"
          autoCapitalize="none"
        />
        {touched.email && errors.email && <Text style={styles.errorText}>{errors.email}</Text>}

        <Text style={styles.label}>Password</Text>
        <View style={styles.passwordContainer}>
          <TextInput
            placeholder="********"
            value={formData.password}
            onChangeText={(text) => handleChange("password", text)}
            onBlur={() => handleBlur("password")}
            style={[getInputStyle("password"), styles.passwordInput]}
            secureTextEntry={!showPassword}
          />
          <TouchableOpacity
            style={styles.eyeIcon}
            onPress={() => setShowPassword(!showPassword)}
          >
            <Ionicons
              name={showPassword ? "eye-off" : "eye"}
              size={20}
              color="#666"
            />
          </TouchableOpacity>
        </View>
        {touched.password && errors.password && <Text style={styles.errorText}>{errors.password}</Text>}

        <TouchableOpacity onPress={() => router.push('/forgetpassword')}>
          <Text style={styles.forgotPasswordText}>Forgot Password?</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.button} onPress={handleLogin} disabled={loading}>
          <Text style={styles.buttonText}>{loading ? "Processing..." : "Log In"}</Text>
        </TouchableOpacity>

        <Text style={styles.text}>
          Don't have an account?{" "}
          <Text style={styles.Link} onPress={() => router.push("/upinscreen")}>
            Go-back
          </Text>
        </Text>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    justifyContent: "center",
    padding: 25,
    backgroundColor: "#fff",
  },
  heading: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#c00808ff",
    textAlign: "center",
    marginBottom: 20,
  },
  label: {
    fontWeight: "bold",
    color: "#333",
    marginBottom: 5,
    marginTop: 10,
  },
  input: {
    backgroundColor: "#f2f2f2",
    borderRadius: 8,
    paddingHorizontal: 15,
    paddingVertical: 10,
    fontSize: 14,
    marginBottom: 5,
    borderWidth: 1,
    borderColor: "#f2f2f2",
  },
  passwordContainer: {
    position: "relative",
    marginBottom: 5,
  },
  passwordInput: {
    paddingRight: 45,
  },
  eyeIcon: {
    position: "absolute",
    right: 15,
    top: 12,
    padding: 5,
  },
  inputError: {
    borderColor: "#ff0000",
  },
  errorText: {
    color: "#ff0000",
    fontSize: 12,
    marginBottom: 5,
  },
  button: {
    backgroundColor: "#d40000",
    paddingVertical: 12,
    borderRadius: 25,
    marginTop: 20,
    marginBottom: 10,
    alignItems: "center",
  },
  buttonText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 16,
  },
  text: {
    textAlign: "center",
    color: "#444",
    marginTop: 10,
  },
  Link: {
    color: "#0000ff",
    textDecorationLine: "underline",
  },
  forgotPasswordText: {
    color: "#0000ff",
    textAlign: "right",
    marginTop: 10,
    marginBottom: 10,
    textDecorationLine: "underline",
    fontSize: 14,
  },

});
