import React, { useState, useRef, useEffect } from 'react';
import { View,  Text,  TextInput,  TouchableOpacity,  StyleSheet,  Alert,  ActivityIndicator,  KeyboardAvoidingView,  Platform,  ScrollView,  Animated} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import * as Yup from 'yup';
import api from '../constants/API';
import { checkAuthStatus } from '../utils/authUtils';

export default function ResetPassword() {
  const router = useRouter();
  const { email } = useLocalSearchParams();
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

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

  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [step, setStep] = useState(1); // 1: OTP verification, 2: Set new password
  
  const inputRefs = useRef([]);
  const fadeAnim = useRef(new Animated.Value(0)).current;



  // Validation schema for password
  const passwordSchema = Yup.object().shape({
    newPassword: Yup.string()
      .min(8, "Password must be at least 8 characters")
      .matches(/[a-z]/, "Password must contain at least one lowercase letter")
      .matches(/[A-Z]/, "Password must contain at least one uppercase letter")
      .matches(/\d/, "Password must contain at least one number")
      .required("Password is required"),
    confirmPassword: Yup.string()
      .oneOf([Yup.ref("newPassword"), null], "Passwords must match")
      .required("Please confirm your password"),
  });

  useEffect(() => {
    
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 500,
      useNativeDriver: true,
    }).start();
  }, []);

  const handleOtpChange = (text, index) => {
    const newOtp = [...otp];
    newOtp[index] = text;
    setOtp(newOtp);

    
    if (text && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }

    setError(''); 
  };

  const handleKeyPress = (e, index) => {
  
    if (e.nativeEvent.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleVerifyOTP = async () => {
    const otpCode = otp.join('');
    
    if (otpCode.length !== 6) {
      setError('Please enter a 6-digit verification code');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await api.post('/donation/verify-reset-otp/', {
        email: email,
        otp: otpCode,
      });

      console.log('OTP verification response:', response.data);
      console.log('Response status:', response.status);

      if (response.status === 200) {
        setStep(2); 
      } else {
        setError(response.data.error || 'Invalid verification code');
      }
    } catch (error) {
      console.error('OTP verification error:', error);
      console.error('Error details:', error.message);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async () => {
    try {
      await passwordSchema.validate({ newPassword, confirmPassword });
      setError('');
    } catch (validationError) {
      setError(validationError.message);
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await api.post('/donation/reset-password/', {
        email: email,
        otp: otp.join(''),
        new_password: newPassword,
      });

      if (response.status === 200) {
        Alert.alert(
          "Password Reset Successful!",
          "Your password has been reset successfully. Please log in with your new password.",
          [
            {
              text: "OK",
              onPress: () => router.replace('/signin')
            }
          ]
        );
      } else {
        setError(response.data.error || 'Failed to reset password');
      }
    } catch (error) {
      console.error('Password reset error:', error);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderOTPStep = () => (
    <>
      <View style={styles.iconContainer}>
        <Ionicons name="lock-closed-outline" size={80} color="#c00808ff" />
      </View>

      <Text style={styles.title}>Verify OTP</Text>
      <Text style={styles.subtitle}>
        We've sent a 6-digit verification code to
      </Text>
      <Text style={styles.email}>{email}</Text>

      <View style={styles.otpContainer}>
        <Text style={styles.otpLabel}>Enter verification code</Text>
        <View style={styles.otpInputs}>
          {otp.map((digit, index) => (
            <TextInput
              key={index}
              ref={(ref) => (inputRefs.current[index] = ref)}
              style={[
                styles.otpInput,
                digit && styles.otpInputFilled,
                error && styles.otpInputError
              ]}
              value={digit}
              onChangeText={(text) => handleOtpChange(text, index)}
              onKeyPress={(e) => handleKeyPress(e, index)}
              keyboardType="numeric"
              maxLength={1}
              selectTextOnFocus
              autoFocus={index === 0}
            />
          ))}
        </View>
        {error && <Text style={styles.errorText}>{error}</Text>}
      </View>

      <TouchableOpacity 
        style={[styles.button, (!otp.join('') || loading) && styles.buttonDisabled]} 
        onPress={handleVerifyOTP}
        disabled={!otp.join('') || loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" size="small" />
        ) : (
          <Text style={styles.buttonText}>Verify OTP</Text>
        )}
      </TouchableOpacity>
    </>
  );

  const renderPasswordStep = () => (
    <>
      <View style={styles.iconContainer}>
        <Ionicons name="key-outline" size={80} color="#c00808ff" />
      </View>

      <Text style={styles.title}>Set New Password</Text>
      <Text style={styles.subtitle}>
        Create a strong password for your account
      </Text>

      <View style={styles.inputContainer}>
        <Text style={styles.label}>New Password</Text>
        <View style={styles.passwordContainer}>
          <TextInput
            style={styles.passwordInput}
            placeholder="Enter new password"
            placeholderTextColor="#999"
            value={newPassword}
            onChangeText={setNewPassword}
            secureTextEntry={!showNewPassword}
            autoCapitalize="none"
          />
          <TouchableOpacity
            style={styles.eyeIcon}
            onPress={() => setShowNewPassword(!showNewPassword)}
          >
            <Ionicons
              name={showNewPassword ? "eye-off" : "eye"}
              size={20}
              color="#666"
            />
          </TouchableOpacity>
        </View>

        <Text style={styles.label}>Confirm New Password</Text>
        <View style={styles.passwordContainer}>
          <TextInput
            style={styles.passwordInput}
            placeholder="Confirm new password"
            placeholderTextColor="#999"
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            secureTextEntry={!showConfirmPassword}
            autoCapitalize="none"
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
        
        {error && <Text style={styles.errorText}>{error}</Text>}
      </View>

      <TouchableOpacity 
        style={[styles.button, (!newPassword || !confirmPassword || loading) && styles.buttonDisabled]} 
        onPress={handleResetPassword}
        disabled={!newPassword || !confirmPassword || loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" size="small" />
        ) : (
          <Text style={styles.buttonText}>Reset Password</Text>
        )}
      </TouchableOpacity>
    </>
  );

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <Animated.View style={[styles.content, { opacity: fadeAnim }]}>
        <View style={styles.header}>
          <TouchableOpacity 
            style={styles.backButton} 
            onPress={() => router.back()}
          >
            <Ionicons name="arrow-back" size={24} color="#333" />
          </TouchableOpacity>
        </View>

        <ScrollView 
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          <View style={styles.mainContent}>
            {step === 1 ? renderOTPStep() : renderPasswordStep()}

            <TouchableOpacity 
              style={styles.backToSignin}
              onPress={() => router.push('/signin')}
            >
              <Text style={styles.backToSigninText}>
                Back to Sign In
              </Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </Animated.View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    flex: 1,
  },
  header: {
    paddingTop: 50,
    paddingHorizontal: 20,
    paddingBottom: 10,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#f8f9fa',
    justifyContent: 'center',
    alignItems: 'center',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingHorizontal: 20,
    paddingBottom: 50,
  },
  mainContent: {
    alignItems: 'center',
  },
  iconContainer: {
    marginBottom: 30,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 5,
  },
  email: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#c00808ff',
    marginBottom: 40,
    textAlign: 'center',
  },
  otpContainer: {
    width: '100%',
    marginBottom: 40,
  },
  otpLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 15,
    textAlign: 'center',
  },
  otpInputs: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 10,
  },
  otpInput: {
    width: 45,
    height: 55,
    borderWidth: 2,
    borderColor: '#ddd',
    borderRadius: 12,
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    backgroundColor: '#f8f9fa',
  },
  otpInputFilled: {
    borderColor: '#c00808ff',
    backgroundColor: '#fff',
  },
  otpInputError: {
    borderColor: '#dc3545',
    backgroundColor: '#fff5f5',
  },
  inputContainer: {
    width: '100%',
    marginBottom: 30,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
    marginTop: 15,
  },
  passwordContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 12,
    backgroundColor: '#f8f9fa',
  },
  passwordInput: {
    flex: 1,
    paddingHorizontal: 15,
    paddingVertical: 15,
    fontSize: 16,
    color: '#333',
  },
  eyeIcon: {
    padding: 15,
  },
  button: {
    backgroundColor: '#c00808ff',
    paddingVertical: 16,
    paddingHorizontal: 40,
    borderRadius: 12,
    marginBottom: 30,
    minWidth: 200,
    alignItems: 'center',
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
    backgroundColor: '#ccc',
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 18,
  },
  errorText: {
    color: '#dc3545',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 10,
  },
  backToSignin: {
    paddingVertical: 10,
  },
  backToSigninText: {
    fontSize: 16,
    color: '#666',
    textDecorationLine: 'underline',
  },
});