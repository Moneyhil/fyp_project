import React, { useState, useEffect } from "react";
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ScrollView, KeyboardAvoidingView, Platform } from "react-native";
import { useRouter } from "expo-router";
import * as Yup from "yup";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Ionicons } from "@expo/vector-icons";
import api from "../constants/API";
import { checkAuthStatus, redirectBasedOnRole } from '../utils/authUtils';

export default function AdminLogin() {
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
    return null; 
  }


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

  const handleAdminLogin = async () => {
    setTouched({ email: true, password: true });
    setLoading(true);

    try {
      await validationSchema.validate(formData, { abortEarly: false });
      setErrors({});

      const response = await api.post(
        "/donation/admin-login/",
        {
          email: formData.email,
          password: formData.password,
        }
      );

      if (response.status === 200) {
        const { token, access_token, refresh_token, user } = response.data;
        const authToken = token || access_token; 

        
        await AsyncStorage.setItem("authToken", authToken);
        if (refresh_token) {
          await AsyncStorage.setItem("refreshToken", refresh_token);
        }
        await AsyncStorage.setItem("userInfo", JSON.stringify(user));

        Alert.alert("Success", "Admin login successful!", [
          {
            text: "OK",
            onPress: () => {
              router.replace("/admindashboard");
            },
          },
        ]);
      }
    } catch (error) {
      console.error("Admin login error:", error);

      if (error.name === "ValidationError") {
        const formErrors = {};
        error.inner.forEach((e) => {
          formErrors[e.path] = e.message;
        });
        setErrors(formErrors);
        Alert.alert("Validation Error", "Please fix the errors in the form.");
      } else if (error.response) {
        const errData = error.response.data;
        let errorMessage = errData?.error || errData?.message || "Admin login failed. Please try again.";
        Alert.alert("Error", errorMessage);
      } else {
        Alert.alert("Error", "An unexpected error occurred. Please try again.");
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
          <Text style={styles.heading}>Admin Sign In</Text>

          <Text style={styles.label}>Admin Email</Text>
          <TextInput
            placeholder="Enter admin email"
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
              placeholder="Enter admin password"
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

          <TouchableOpacity
            style={[styles.button, loading && styles.buttonDisabled]}
            onPress={handleAdminLogin}
            disabled={loading}
          >
            <Text style={styles.buttonText}>{loading ? "Signing In..." : "Admin Sign In"}</Text>
          </TouchableOpacity>

          <TouchableOpacity onPress={() => router.push("/upinscreen")}>
            <Text style={styles.text}>
              Back to <Text style={styles.Link}>Main Screen</Text>
            </Text>
          </TouchableOpacity>
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
  buttonDisabled: {
    backgroundColor: "#ccc",
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