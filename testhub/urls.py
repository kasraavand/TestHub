"""testhub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path
from orchestrator import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'', views.BaseRedirect.as_view()),
    path(r'home/<int:page>', views.Home.as_view(), name='home'),
    path(r'accounts/login/', views.login, name='login'),
    path(r'logout/', auth_views.logout, name='logout', kwargs={'next_page': '/'}),
    path(r'signup/', views.signup_view, name='signup'),
    path(r'filtered/<str:request_type>/<int:page>', views.SpecificRequests.as_view(), name='filtered_request'),
    path(r'filtered/<int:page>', views.SpecificRequests.as_view(), name='filtered_request'),
    path(r'record_status/<int:record_id>', views.RecordStatus.as_view(), name='record_status')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)