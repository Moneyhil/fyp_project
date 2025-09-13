import React, { useState, useEffect, useRef } from 'react';
import {   View,   Text,   TextInput,   TouchableOpacity,   StyleSheet,   Alert,   Dimensions,  ActivityIndicator,  KeyboardAvoidingView,  Platform,  Animated,  ScrollView} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import api from '../constants/API';

const { width, height } = Dimensions.get('window');

export default function OTPVerification() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const email = params.email || '';

  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const inputRefs = useRef([]);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  // API Endpoints
  const API_ENDPOINTS = {
    VERIFY_OTP: '/donation/verify-otp/',
    SEND_OTP: '/donation/send-otp/',
  };

  useEffect(() => {
    // Fade in animation
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 500,
      useNativeDriver: false, 
    }).start();

    
    startCountdown();
  }, []);

  useEffect(() => {
    let timer;
    if (countdown > 0) {
      timer = setTimeout(() => setCountdown(countdown - 1), 1000);
    }
    return () => clearTimeout(timer);
  }, [countdown]);

  const startCountdown = () => {
    setCountdown(60); 
  };

  const handleOtpChange = (text, index) => {
    const newOtp = [...otp];
    newOtp[index] = text;
    setOtp(newOtp);

    
    if (text && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }

    
    const fullOtp = newOtp.join('');
    if (fullOtp.length === 6 && !fullOtp.includes('') && !isSubmitting && !loading) {
      
      setTimeout(() => {
        if (!isSubmitting && !loading) {
          handleVerifyOTP(fullOtp);
        }
      }, 100);
    }

    setError(''); 
  };

  const handleKeyPress = (e, index) => {
    
    if (e.nativeEvent.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleVerifyOTP = async (otpCode = null) => {
    if (isSubmitting) return;

    const otpToVerify = otpCode || otp.join('');
    
    if (otpToVerify.length !== 6) {
      setError('Please enter a 6-digit verification code');
      return;
    }

    setIsSubmitting(true);
    setLoading(true);
    setError('');

    try {
      const response = await api.post(
        API_ENDPOINTS.VERIFY_OTP,
        {
          email: email,
          otp: otpToVerify,
        }
      );

      console.log('OTP verification response:', response.data);

      if (response.status === 200) {
    
        await AsyncStorage.removeItem('pendingVerificationEmail');
        
        
        const { user, token, access_token, refresh_token } = response.data;
        
        if (user) {
          await AsyncStorage.setItem('userInfo', JSON.stringify(user));
        }
        
  
        const authToken = token || access_token;
        if (authToken) {
          await AsyncStorage.setItem('authToken', authToken);
        }
        
        if (refresh_token) {
          await AsyncStorage.setItem('refreshToken', refresh_token);
        }
        
        Alert.alert(
          "Verification Successful!",
          "Your email has been verified. Please complete your profile!",
          [
            {
              text: "Continue",
              onPress: () => router.replace('/profile')
            }
          ]
        );
      }
    } catch (error) {
      console.error('OTP verification error:', error);
      
      if (error.response) {
        const errorData = error.response.data;
        let errorMessage = 'Verification failed. Please try again.';
        
        if (errorData) {
    
          if (errorData.error) {
            errorMessage = Array.isArray(errorData.error) ? errorData.error[0] : errorData.error;
          } else if (errorData.otp) {
            errorMessage = Array.isArray(errorData.otp) ? errorData.otp[0] : errorData.otp;
          } else if (errorData.email) {
            errorMessage = Array.isArray(errorData.email) ? errorData.email[0] : errorData.email;
          } else if (errorData.detail) {
            errorMessage = errorData.detail;
          }
        }
        
        setError(errorMessage);
      } else if (error.code === 'ECONNABORTED') {
        setError('Request timed out. Please check your internet connection.');
      } else if (error.code === 'NETWORK_ERROR' || error.message.includes('Network Error')) {
        setError('Network error. Please check your internet connection.');
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
      setIsSubmitting(false);
    }
  };

  const handleResendOTP = async () => {
    if (resendLoading || countdown > 0) return;

    setResendLoading(true);
    setError('');

    try {
      const response = await api.post(
        API_ENDPOINTS.SEND_OTP,
        {
          email: email,
        }
      );

      if (response.status === 200) {
        Alert.alert(
          "OTP Sent",
          "A new verification code has been sent to your email.",
          [{ text: "OK" }]
        );
        startCountdown();
        setOtp(['', '', '', '', '', '']); 
        inputRefs.current[0]?.focus(); 
      }
    } catch (error) {
      console.error('Resend OTP error:', error);
      
      if (error.response) {
        const errorData = error.response.data;
        let errorMessage = 'Failed to resend OTP. Please try again.';
        
        if (errorData) {
        
          if (errorData.error) {
            errorMessage = Array.isArray(errorData.error) ? errorData.error[0] : errorData.error;
          } else if (errorData.email) {
            errorMessage = Array.isArray(errorData.email) ? errorData.email[0] : errorData.email;
          } else if (errorData.detail) {
            errorMessage = errorData.detail;
          }
        }
        
        setError(errorMessage);
      } else {
        setError('Network error. Please check your internet connection.');
      }
    } finally {
      setResendLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

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
          <View style={styles.iconContainer}>
            <Ionicons name="mail-outline" size={80} color="#c00808ff" />
          </View>

          <Text style={styles.title}>Verify Your Email</Text>
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
            style={[styles.verifyButton, (!otp.join('') || loading) && styles.verifyButtonDisabled]} 
            onPress={() => handleVerifyOTP()}
            disabled={!otp.join('') || loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" size="small" />
            ) : (
              <Text style={styles.verifyButtonText}>Verify Email</Text>
            )}
          </TouchableOpacity>

          <View style={styles.resendContainer}>
            <Text style={styles.resendText}>Didn't receive the code? </Text>
            {countdown > 0 ? (
              <Text style={styles.countdownText}>
                Resend in {formatTime(countdown)}
              </Text>
            ) : (
              <TouchableOpacity 
                onPress={handleResendOTP}
                disabled={resendLoading}
                style={styles.resendButton}
              >
                {resendLoading ? (
                  <ActivityIndicator color="#c00808ff" size="small" />
                ) : (
                  <Text style={styles.resendButtonText}>Resend Code</Text>
                )}
              </TouchableOpacity>
            )}
          </View>

          <TouchableOpacity 
            style={styles.backToSignup}
            onPress={() => router.push('/signup')}
          >
            <Text style={styles.backToSignupText}>
              Back to Sign Up
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
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingBottom: 20,
  },
  header: {
    paddingTop: 50,
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#f8f9fa',
    justifyContent: 'center',
    alignItems: 'center',
  },
  mainContent: {
    flex: 1,
    paddingHorizontal: 30,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: height - 150,
  },
  iconContainer: {
    marginBottom: 30,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 10,
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
    textAlign: 'center',
    marginBottom: 40,
  },
  otpContainer: {
    width: '100%',
    marginBottom: 30,
  },
  otpLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 20,
  },
  otpInputs: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  otpInput: {
    width: 50,
    height: 60,
    borderWidth: 2,
    borderColor: '#e9ecef',
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
  errorText: {
    color: '#dc3545',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 10,
  },
  verifyButton: {
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
  verifyButtonDisabled: {
    backgroundColor: '#ccc',
  },
  verifyButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 18,
  },
  resendContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 30,
  },
  resendText: {
    fontSize: 16,
    color: '#666',
  },
  resendButton: {
    paddingVertical: 5,
  },
  resendButtonText: {
    fontSize: 16,
    color: '#c00808ff',
    fontWeight: 'bold',
    textDecorationLine: 'underline',
  },
  countdownText: {
    fontSize: 16,
    color: '#999',
    fontWeight: 'bold',
  },
  backToSignup: {
    paddingVertical: 10,
  },
  backToSignupText: {
    fontSize: 16,
    color: '#666',
    textDecorationLine: 'underline',
  },
});
