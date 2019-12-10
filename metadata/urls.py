"""metadata URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.views.static import serve
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy
from django.conf.urls.static import static
from .api import router



urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('mydatasets.urls')),
    url(r'^mydatasets/', include('mydatasets.urls', namespace='mydatasets')),
    url(r'^accounts/login/$', login, name='login'),
    url(r'^accounts/logout/$', logout, name='logout'),
    url(r'^login/$', auth_views.login, {'template_name': 'mydatasets/templates/mydatasets/login.html'},
        name='meta_login'),
    url(r'^logout/$', auth_views.logout,
        {'next_page': reverse_lazy('dataset_list')}, name='meta_logout'),
    url(r'^oauth/', include('social_django.urls', namespace='social')), # social
    url(r'^api/', include(router.urls)), # api
    # url(r'api/auth/', include('djoser.urls.authtoken')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
