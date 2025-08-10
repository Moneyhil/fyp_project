from django.urls import path 
from .views import Admin1List, Signup1Create, Signup1List
 # Import directly, so we don't need `views.`

urlpatterns = [
    path('Admin1/', Admin1List.as_view(), name='Admin1list'),
    path('Signup1/create/', Signup1Create.as_view(), name='Signup1create'),
    path('Signup1/list/', Signup1List.as_view(), name='Signup1list'),
]
