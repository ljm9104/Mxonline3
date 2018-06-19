from django.conf.urls import url

from users.views import LoginView

urlpatterns = [
    # 登录页面跳转url login不要直接调用。而只是指向这个函数对象。
    url('^login/$', LoginView.as_view(), name="login"),

]
