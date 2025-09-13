import React, { useState, useEffect } from "react";
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ScrollView, KeyboardAvoidingView, Platform } from "react-native";
import { useRouter } from "expo-router";
import * as Yup from "yup";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Ionicons } from "@expo/vector-icons";
import api from "../constants/API";
import { checkAuthStatus } from "../utils/authUtils";

export default function Registration() {
  const router = useRouter();
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

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

  
  const validationSchema = Yup.object().shape({
    name: Yup.string()
      .trim()
      .min(2, "Name must be at least 2 characters")
      .max(50, "Name must be at most 50 characters")
      .matches(/^[a-zA-Z\s]+$/, "Name can only contain letters and spaces")
      .required("Full name is required"),
    email: Yup.string()
      .trim()
      .email("Please enter a valid email address")
      .max(50, "Email must be at most 50 characters")
      .required("Email address is required"),
    password: Yup.string()
      .min(8, "Password must be at least 8 characters")
      .max(50, "Password must be at most 50 characters")
      .matches(/[a-z]/, "Password must contain at least one lowercase letter")
      .matches(/[A-Z]/, "Password must contain at least one uppercase letter")
      .matches(/\d/, "Password must contain at least one number")
      .matches(/[!@#$%^&*(),.?":{}|<>]/, "Password must contain at least one special character")
      .required("Password is required"),
    confirmPassword: Yup.string()
      .oneOf([Yup.ref("password"), null], "Passwords must match")
      .required("Please confirm your password"),
  });

  const handleChange = (field, value) => {
    setFormData(prev => {
      const updated = { ...prev, [field]: value };
      if (touched[field]) {
        validationSchema
          .validateAt(field, updated)
          .then(() => setErrors(prev => ({ ...prev, [field]: "" })))
          .catch(err => setErrors(prev => ({ ...prev, [field]: err.message })));
      }
      return updated;
    });
  };

  const handleBlur = (field) => setTouched(prev => ({ ...prev, [field]: true }));

  const getInputStyle = (field) => touched[field] && errors[field] ? [styles.input, styles.inputError] : styles.input;

  
  const testConnection = async () => {
    try {
      const response = await api.get('/donation/health-check/', { timeout: 5000 });
      console.log('Backend connection successful:', response.status);
      return true;
    } catch (error) {
      console.error('Backend connection failed:', error.message);
      Alert.alert(
        "Backend Connection Failed", 
        "Cannot connect to the backend server. Please ensure:\n\n• Backend server is running\n• Network connection is stable\n• Server IP is correct"
      );
      return false;
    }
  };

  const handleSignup = async () => {
    
    const isConnected = await testConnection();
    if (!isConnected) {
      return;
    }

    setTouched({ name: true, email: true, password: true, confirmPassword: true });
    setLoading(true);

    try {
      await validationSchema.validate(formData, { abortEarly: false });
      setErrors({});

      const payload = {
        name: formData.name.trim(),
        email: formData.email.trim().toLowerCase(),
        password: formData.password,
      };

    
      const response = await api.post(
        "/donation/registration/create/",
        payload
      );

      if (response.status === 201) {

        await AsyncStorage.setItem("pendingVerificationEmail", payload.email);

        Alert.alert(
          "Registration Successful!",
          "Please check your email for the verification code.",
          [
            {
              text: "OK",
              onPress: () => {
                
                router.push({ pathname: "/otp", params: { email: payload.email } });
              },
            },
          ]
        );
      }

    } catch (error) {
      console.error("Signup error:", error);
      console.error("Error code:", error.code);
      console.error("Error message:", error.message);
      
      
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
    
        Alert.alert(
          "Connection Timeout", 
          "The server is taking too long to respond. This might be due to:\n\n• Backend server not running\n• Network connectivity issues\n• Email sending delays\n\nPlease check your connection and try again.",
          [
            { text: "Retry", onPress: () => handleSignup() },
            { text: "Cancel", style: "cancel" }
          ]
        );
      } else if (error.code === 'NETWORK_ERROR' || error.message.includes('Network Error')) {
      
        Alert.alert(
          "Network Error", 
          "Cannot connect to the server. Please check:\n\n• Your internet connection\n• Backend server is running\n• Server IP address is correct",
          [
            { text: "Retry", onPress: () => handleSignup() },
            { text: "Cancel", style: "cancel" }
          ]
        );
      } else if (error.name === "ValidationError") {
        const formErrors = {};
        error.inner.forEach(e => { formErrors[e.path] = e.message; });
        setErrors(formErrors);
        Alert.alert("Validation Error", "Please fix the errors in the form.");
      } else if (error.response) {
        const errData = error.response.data;
        
      
        if (errData.password) {
          setErrors(prev => ({ ...prev, password: Array.isArray(errData.password) ? errData.password[0] : errData.password }));
          Alert.alert("Password Error", Array.isArray(errData.password) ? errData.password[0] : errData.password);
        } else if (errData.email) {
          setErrors(prev => ({ ...prev, email: Array.isArray(errData.email) ? errData.email[0] : errData.email }));
          Alert.alert("Email Error", Array.isArray(errData.email) ? errData.email[0] : errData.email);
        } else if (errData.name) {
          setErrors(prev => ({ ...prev, name: Array.isArray(errData.name) ? errData.name[0] : errData.name }));
          Alert.alert("Name Error", Array.isArray(errData.name) ? errData.name[0] : errData.name);
        } else {
          let errorMessage = errData?.error || errData?.message || "Registration failed. Please try again.";
          if (error.response.status === 409) {
            setErrors(prev => ({ ...prev, email: "This email is already registered" }));
            Alert.alert("Email Already Exists", "This email is already registered. Please use a different email or try logging in.");
          } else if (error.response.status === 400) {
            Alert.alert("Validation Error", "Please check your input and try again.");
          } else {
            Alert.alert("Error", errorMessage);
          }
        }
      } else {
        Alert.alert(
          "Unexpected Error", 
          "An unexpected error occurred. Please try again.\n\nIf the problem persists, please contact support."
        );
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
          <Text style={styles.heading}>Sign Up</Text>

        <Text style={styles.label}>Full Name</Text>
        <TextInput
          placeholder="Enter your full name"
          value={formData.name}
          onChangeText={(text) => handleChange("name", text)}
          onBlur={() => handleBlur("name")}
          style={getInputStyle("name")}
          autoCapitalize="words"
        />
        {touched.name && errors.name && <Text style={styles.errorText}>{errors.name}</Text>}

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
            placeholder="Create a strong password"
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

        <Text style={styles.label}>Confirm Password</Text>
        <View style={styles.passwordContainer}>
          <TextInput
            placeholder="Confirm your password"
            value={formData.confirmPassword}
            onChangeText={(text) => handleChange("confirmPassword", text)}
            onBlur={() => handleBlur("confirmPassword")}
            style={[getInputStyle("confirmPassword"), styles.passwordInput]}
            secureTextEntry={!showConfirmPassword}
          />
          <TouchableOpacity
            style={styles.eyeIcon}
            onPress={() => setShowConfirmPassword(!showConfirmPassword)}
          >
            <Ionicons
              name={showConfirmPassword ? "eye-off" : "eye"}
              size={20}
              color="#666"
            />
          </TouchableOpacity>
        </View>
        {touched.confirmPassword && errors.confirmPassword && <Text style={styles.errorText}>{errors.confirmPassword}</Text>}

        <TouchableOpacity style={styles.button} onPress={handleSignup} disabled={loading}>
          <Text style={styles.buttonText}>{loading ? "Processing..." : "Sign Up"}</Text>
        </TouchableOpacity>

        <Text style={styles.text}>
          Already have an account?{" "}
          <Text style={styles.Link} onPress={() => router.push("/signin")}>
            Log In
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
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
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
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
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
  passwordContainer: {
    position: "relative",
  },
  passwordInput: {
    paddingRight: 45,
  },
  eyeIcon: {
    position: "absolute",
    right: 15,
    top: 12,
    zIndex: 1,
  },
});
