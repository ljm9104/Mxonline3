from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.shortcuts import render

from users.models import UserProfile


# 自定义authenticate方法,  实现用户名邮箱均可登录,继承ModelBackend类，因为它有方法authenticate
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 不希望用户存在两个，get只能有一个。Q为使用并集查询
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            # django的后台中密码加密：所以不能password==password
            # UserProfile继承的AbstractUser中有 check_password(self, raw_password):
            if user.check_password():
                return user
        except Exception as e:
            print(e)
            return None


# Django默认我们使用用户名和密码来登录，用Django提供的login，用于登陆验证，用user_login区分
def user_login(request):
    # 前端向后端发送的请求方式: get 或post, 提交表单post
    if request.method == "POST":
        user_name = request.POST.get("username", "")
        pass_word = request.POST.get("password", "")
        # 成功返回user对象, 失败返回null
        user = authenticate(username=user_name, password=pass_word)
        if user is not None:
            # login两参数：request, user, 实际是对request写了一部分东西进去， request是要render回去的，返回浏览器。完成登录
            login(request, user)
            return render(request, "index.html")
        else:
            return render(request, "login.html", {"msg": "用户名或者密码错误"})

    elif request.method == "GET":
        # render就是渲染html返回用户, render三变量: request 模板名称 一个字典写明传给前端的值
        return render(request, "login.html", {})
