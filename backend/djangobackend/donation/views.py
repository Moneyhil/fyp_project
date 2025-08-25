from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit
import logging
import json
from datetime import datetime, timedelta

from .models import User, Profile, Admin, DonationRequest, CallLog, MonthlyDonationTracker
from .serializers import (
    UserSerializer, 
    OTPVerifySerializer, 
    SendOTPSerializer, 
    LoginSerializer, 
    UserResponseSerializer,
    ProfileSerializer,
    DonationRequestSerializer,
    CallLogSerializer,
    DonationRequestResponseSerializer
)
from .services import DonationRequestService
from .email_config import EmailService

logger = logging.getLogger(__name__)

class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', method='POST')
def send_otp(request):
    serializer = SendOTPSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.user
        raw_otp = user.generate_otp()
        
        try:
            send_mail(
                subject='Your Verification Code',
                message=f'Your OTP: {raw_otp}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            return Response({'message': 'OTP sent successfully'})
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return Response({'error': 'Failed to send OTP'}, status=500)
    
    return Response(serializer.errors, status=400)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            return Response({
                'message': 'Email verified successfully',
                'user': UserResponseSerializer(user).data,
                'token': access_token,
                'refresh_token': str(refresh)
            })
        
        return Response(serializer.errors, status=400)

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            return Response({
                'message': 'Login successful',
                'user': UserResponseSerializer(user).data,
                'token': access_token,
                'refresh_token': str(refresh)
            })
        
        return Response(serializer.errors, status=400)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({'message': 'Logout successful'})
        except Exception as e:
            return Response({'error': 'Invalid token'}, status=400)

# Admin Authentication Views
class AdminLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=400)
        
        try:
            # Check if user exists and is staff
            user = User.objects.get(email=email, is_staff=True)
            
            if user.check_password(password):
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                
                # Update last login
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
                
                return Response({
                    'message': 'Admin login successful',
                    'user': UserResponseSerializer(user).data,
                    'token': access_token,
                    'refresh_token': str(refresh)
                })
            else:
                return Response({'error': 'Invalid credentials'}, status=401)
                
        except User.DoesNotExist:
            return Response({'error': 'Invalid admin credentials'}, status=401)

class AdminLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({'message': 'Admin logout successful'})
        except Exception as e:
            return Response({'error': 'Invalid token'}, status=400)

class AdminCreateView(APIView):
    permission_classes = [AllowAny]  # You might want to restrict this
    
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not all([name, email, password]):
            return Response({'error': 'Name, email and password are required'}, status=400)
        
        try:
            # Create admin user
            admin_user = User.objects.create_user(
                name=name,
                email=email,
                password=password,
                is_staff=True,
                is_superuser=True,
                is_verified=True
            )
            
            return Response({
                'message': 'Admin created successfully',
                'user': UserResponseSerializer(admin_user).data
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class AdminForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Implementation for admin password reset
        return Response({'message': 'Admin password reset functionality'})

class AdminResetPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Implementation for admin password reset
        return Response({'message': 'Admin password reset functionality'})

# User Management Views (Admin only)
class UserListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, status=403)
        
        users = User.objects.filter(is_staff=False).order_by('-date_joined')
        users_data = []
        
        for user in users:
            users_data.append({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'is_active': user.is_active,
                'is_verified': user.is_verified,
                'date_joined': user.date_joined
            })
        
        return Response({'users': users_data})

class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, status=403)
        
        try:
            user = User.objects.get(pk=pk, is_staff=False)
            user.delete()
            return Response({'message': 'User deleted successfully'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

class BlockUnblockUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, status=403)
        
        try:
            user = User.objects.get(pk=pk, is_staff=False)
            user.is_active = not user.is_active
            user.save()
            
            action = 'unblocked' if user.is_active else 'blocked'
            return Response({'message': f'User {action} successfully'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

class RevokeAccessView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, status=403)
        
        try:
            user = User.objects.get(pk=pk, is_staff=False)
            user.is_verified = False
            user.save()
            return Response({'message': 'User access revoked successfully'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

class BlockedProfilesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, status=403)
        
        # Get all inactive users (blocked users)
        blocked_users = User.objects.filter(
            is_staff=False, 
            is_active=False
        ).order_by('-date_joined')
        
        blocked_profiles_data = []
        
        for user in blocked_users:
            # Try to get monthly tracker info if available
            tracker_info = None
            try:
                current_month = timezone.now().date().replace(day=1)
                tracker = MonthlyDonationTracker.objects.filter(
                    user=user,
                    month=current_month
                ).first()
                
                if tracker:
                    tracker_info = {
                        'completed_calls_count': tracker.completed_calls_count,
                        'monthly_goal_completed': tracker.monthly_goal_completed,
                        'goal_completed_at': tracker.goal_completed_at,
                        'month': tracker.month.strftime('%B %Y')
                    }
            except Exception as e:
                logger.error(f"Error getting tracker info for user {user.id}: {e}")
            
            blocked_profiles_data.append({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'is_active': user.is_active,
                'is_verified': user.is_verified,
                'date_joined': user.date_joined,
                'tracker_info': tracker_info
            })
        
        return Response({
            'blocked_profiles': blocked_profiles_data,
            'count': len(blocked_profiles_data)
        })

# Password Reset Views
class UserForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=400)
        
        try:
            user = User.objects.get(email=email)
            raw_otp = user.generate_otp()
            
            try:
                send_mail(
                    subject='Password Reset Code',
                    message=f'Your password reset code: {raw_otp}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )
                return Response({'message': 'Password reset code sent to your email'})
            except Exception as e:
                logger.error(f"Email send failed: {e}")
                return Response({'error': 'Failed to send reset code'}, status=500)
                
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=404)

class UserVerifyResetOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        if not email or not otp:
            return Response({'error': 'Email and OTP are required'}, status=400)
        
        try:
            user = User.objects.get(email=email)
            is_valid, message = user.verify_otp(otp)
            
            if is_valid:
                return Response({'message': 'OTP verified successfully'})
            else:
                return Response({'error': message}, status=400)
                
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

class UserResetPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        
        if not all([email, otp, new_password]):
            return Response({'error': 'Email, OTP and new password are required'}, status=400)
        
        try:
            user = User.objects.get(email=email)
            is_valid, message = user.verify_otp(otp)
            
            if is_valid:
                user.set_password(new_password)
                user.save()
                return Response({'message': 'Password reset successfully'})
            else:
                return Response({'error': message}, status=400)
                
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

# Profile Views
class ProfileCreateView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            email = request.data.get('email')
            if not email:
                return Response({'error': 'Email is required'}, status=400)
            
            user = User.objects.get(email=email)
            
            # Check if profile already exists
            if hasattr(user, 'profile'):
                return Response({'error': 'Profile already exists'}, status=400)
            
            # Create profile
            profile_data = {
                'first_name': request.data.get('first_name'),
                'last_name': request.data.get('last_name'),
                'contact_number': request.data.get('contact_number'),
                'address': request.data.get('address'),
                'gender': request.data.get('gender'),
                'city': request.data.get('city'),
                'blood_group': request.data.get('blood_group'),
                'role': request.data.get('role'),
            }
            
            profile = Profile.objects.create(user=user, **profile_data)
            serializer = ProfileSerializer(profile)
            
            return Response({
                'message': 'Profile created successfully',
                'profile': serializer.data
            }, status=201)
            
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class ProfileDetailView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, email):
        try:
            user = User.objects.get(email=email)
            profile = user.profile
            serializer = ProfileSerializer(profile)
            
            return Response({
                'profile': serializer.data
            })
            
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=404)

# Donor Search View
class DonorSearchView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        blood_group = request.GET.get('blood_group')
        city = request.GET.get('city')
        
        if not blood_group or not city:
            return Response({'error': 'Blood group and city are required'}, status=400)
        
        try:
            # Find donors with matching criteria who are active and verified
            donors = Profile.objects.filter(
                blood_group=blood_group,
                city=city,
                role='donor',
                user__is_active=True,
                user__is_verified=True
            ).select_related('user')
            
            donors_data = []
            for donor in donors:
                donors_data.append({
                    'id': donor.id,
                    'user': donor.user.id,
                    'full_name': donor.full_name,
                    'blood_group': donor.blood_group,
                    'city': donor.city,
                    'contact_number': donor.contact_number,
                    'address': donor.address,
                    'gender': donor.gender
                })
            
            return Response({
                'donors': donors_data,
                'count': len(donors_data)
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# Donation Request Views
class DonationRequestCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            serializer = DonationRequestSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                donation_request = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Donation request created successfully',
                    'donation_request_id': donation_request.id
                }, status=201)
            return Response(serializer.errors, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class DonationRequestListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get requests where user is either requester or donor
        requests = DonationRequest.objects.filter(
            Q(requester=request.user) | Q(donor=request.user)
        ).order_by('-created_at')
        
        serializer = DonationRequestSerializer(requests, many=True)
        return Response({'donation_requests': serializer.data})

class DonationRequestResponseView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, request_id):
        try:
            donation_request = DonationRequest.objects.get(id=request_id)
            
            # Check if user is involved in this request
            if request.user not in [donation_request.requester, donation_request.donor]:
                return Response({'error': 'Access denied'}, status=403)
            
            serializer = DonationRequestResponseSerializer(data=request.data)
            if serializer.is_valid():
                response = serializer.validated_data['response']
                notes = serializer.validated_data.get('notes', '')
                
                # Update the appropriate response field
                if request.user == donation_request.requester:
                    donation_request.user_response = response
                elif request.user == donation_request.donor:
                    donation_request.donor_response = response
                
                donation_request.save()
                donation_request.update_status()
                
                # Send notification
                DonationRequestService.send_response_notification(
                    donation_request, request.user, response, notes
                )
                
                return Response({'message': 'Response recorded successfully'})
            
            return Response(serializer.errors, status=400)
            
        except DonationRequest.DoesNotExist:
            return Response({'error': 'Donation request not found'}, status=404)

# Monthly Tracker View
class MonthlyTrackerView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        user_email = request.GET.get('user_email')
        if not user_email:
            return Response({'error': 'User email is required'}, status=400)
        
        try:
            user = User.objects.get(email=user_email)
            current_month = timezone.now().date().replace(day=1)
            
            tracker, created = MonthlyDonationTracker.get_or_create_for_user_month(
                user=user,
                date=current_month
            )
            
            return Response({
                'user_email': user_email,
                'month': tracker.month.strftime('%B %Y'),
                'completed_calls_count': tracker.completed_calls_count,
                'monthly_goal_completed': tracker.monthly_goal_completed,
                'goal_completed_at': tracker.goal_completed_at,
                'created': created
            })
            
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

# Donor Response View (for email links)
class DonorResponseView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, request_id, response):
        try:
            donation_request = DonationRequest.objects.get(id=request_id)
            
            # Update donor response
            if response.lower() == 'yes':
                donation_request.donor_response = True
            elif response.lower() == 'no':
                donation_request.donor_response = False
            else:
                return Response({'error': 'Invalid response'}, status=400)
            
            donation_request.save()
            donation_request.update_status()
            
            return Response({
                'message': f'Thank you for your response. You have {response.lower()} to donate blood.'
            })
            
        except DonationRequest.DoesNotExist:
            return Response({'error': 'Donation request not found'}, status=404)

# Call Log Views
class CallLogCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            serializer = CallLogSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                call_log = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Call logged successfully',
                    'call_log': {
                        'id': call_log.id,
                        'caller': call_log.caller.id,
                        'receiver': call_log.receiver.id,
                        'call_status': call_log.call_status,
                        'created_at': call_log.created_at
                    }
                }, status=201)
            return Response(serializer.errors, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# Notification Views
class SendDonorNotificationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            call_log_id = request.data.get('call_log_id')
            donor_agreed = request.data.get('donor_agreed', False)
            
            if not call_log_id:
                return Response({'error': 'Call log ID is required'}, status=400)
            
            # Get the call log
            call_log = CallLog.objects.get(id=call_log_id)
            
            if donor_agreed:
                # Send email to donor asking for confirmation
                success, message = EmailService.send_donor_confirmation_email(
                    call_log.receiver,  # donor
                    call_log.caller,    # caller
                    call_log_id
                )
                
                if success:
                    # Update call log to mark email as sent
                    call_log.email_sent = True
                    call_log.email_sent_at = timezone.now()
                    call_log.save()
                    
                    return Response({
                        'success': True,
                        'message': 'Donor notification sent successfully'
                    })
                else:
                    return Response({'error': message}, status=500)
            else:
                return Response({
                    'success': True,
                    'message': 'No notification needed for declined donation'
                })
                
        except CallLog.DoesNotExist:
            return Response({'error': 'Call log not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# Donor Email Confirmation View
class DonorEmailConfirmationView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        call_log_id = request.GET.get('call_log_id')
        response = request.GET.get('response')
        
        if not call_log_id or not response:
            return Response({'error': 'Call log ID and response are required'}, status=400)
        
        try:
            call_log = CallLog.objects.get(id=call_log_id)
            
            # Update donor email response
            if response.lower() == 'yes':
                call_log.donor_email_response = 'yes'
                call_log.receiver_confirmed = True
                
                # Update monthly tracker for the donor
                current_month = timezone.now().date().replace(day=1)
                tracker, created = MonthlyDonationTracker.get_or_create_for_user_month(
                    user=call_log.receiver,
                    date=current_month
                )
                
                # Increment call count and check if monthly goal is reached
                goal_completed = tracker.increment_call_count()
                
                if goal_completed:
                    # Block the user if they completed 3 calls
                    call_log.receiver.is_active = False
                    call_log.receiver.save()
                
            elif response.lower() == 'no':
                call_log.donor_email_response = 'no'
                call_log.receiver_confirmed = False
            
            call_log.email_response_at = timezone.now()
            call_log.save()
            
            # Check if both parties confirmed
            call_log.mark_both_confirmed()
            
            return Response({
                'success': True,
                'message': f'Thank you for your response. You have {response.lower()} to donate blood.'
            })
            
        except CallLog.DoesNotExist:
            return Response({'error': 'Call log not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)