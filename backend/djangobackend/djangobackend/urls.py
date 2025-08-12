from django.contrib import admin
from django.urls import path, include
from donation import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('donation/', include('donation.urls')),
]
