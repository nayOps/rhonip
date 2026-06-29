"""
URL configuration for payday project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from notifications import urls
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import re_path
from django.views.static import serve

from core.views.login import EmployeeLogin

urlpatterns = [
    path('tinymce/', include('tinymce.urls')),
    path('login/', EmployeeLogin.as_view(), name='login'),
    path('', include('django.contrib.auth.urls')),
    
    path('', include('core.urls')),
    path('api/', include('api.urls')),
    path('mission/', include('mission.urls')),
    path('employee/', include('employee.urls')),
    path('notifications', include(urls, namespace='notifications')),
]

if settings.DEBUG:
    urlpatterns.append(path('buple/', admin.site.urls))
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))

urlpatterns += staticfiles_urlpatterns()

# Prod : secours si WhiteNoise / collectstatic ne livre pas les assets (évite CSS en text/html).
if not settings.DEBUG:
    static_prefix = settings.STATIC_URL.lstrip('/').rstrip('/')
    if static_prefix:
        urlpatterns += [
            re_path(
                rf'^{static_prefix}/(?P<path>.*)$',
                serve,
                {'document_root': settings.STATIC_ROOT},
            ),
        ]

# static() n'enregistre les médias que si DEBUG=1 — en prod on sert /media/ explicitement
media_prefix = settings.MEDIA_URL.lstrip('/').rstrip('/')
if media_prefix:
    urlpatterns += [
        re_path(
            rf'^{media_prefix}/(?P<path>.*)$',
            serve,
            {'document_root': settings.MEDIA_ROOT},
        ),
    ]
elif settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)