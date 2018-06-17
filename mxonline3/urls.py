"""mxonline3 URL Configuration

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
import xadmin
from django.conf.urls import url
# from django.contrib import admin
from django.views.generic import TemplateView, RedirectView

from users.views import LoginView

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    # 首页
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    # 网站的图标
    url(r'^favicon.ico$', RedirectView.as_view(url=r'static/favicon.ico')),
    # 登陆页面
    # url(r'^login/$', TemplateView.as_view(template_name='login.html'), name='login'),
    # url(r'^login/$', user_login, name='login'),
    url('^login/$', LoginView.as_view(), name="login"),
    # 注册
    url(r'^register/$', TemplateView.as_view(template_name='register.html'), name='register'),

]
