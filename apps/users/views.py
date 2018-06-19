from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View

from users.forms import LoginForm, RegisterForm
from users.models import UserProfile, EmailVerifyRecord

# 自定义authenticate方法,  实现用户名邮箱均可登录,继承ModelBackend类，因为它有方法authenticate
from utils.email_send import send_register_eamil


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


# 基于类的方法登陆
class LoginView(View):
    # 直接调用get方法免去判断
    def get(self, request):
        return render(request, "login.html", {})

    def post(self, request):
        # 类实例化需要一个字典参数request.POST就是一个QueryDict所以直接传入,POST中的username, password，会对应到form中
        login_form = LoginForm(request.POST)
        # is_valid判断我们字段是否有错执行我们原有逻辑，验证失败跳回login页面
        if login_form.is_valid():
            # 取不到时为空，username，password为前端页面name值
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")

            # 成功返回user对象,失败返回null
            user = authenticate(username=user_name, password=pass_word)

            if user is not None:
                login(request, user)
                # 跳转到首页 user request会被带回到首页
                return render(request, "index.html")
            # 验证不成功跳回登录页面, 没有成功说明里面的值是None，并再次跳转回主页面
            else:
                return render(request, "login.html", {"msg": "用户名或密码错误! "})
        else:
            return render(request, "login.html", {'login_form': login_form})

    '''def post(self, request):
        # 取不到时为空，username，password为前端页面name值
        user_name = request.POST.get("username", "")
        pass_word = request.POST.get("password", "")
        user = authenticate(username=user_name, password=pass_word)

        if user is not None:
            login(request, user)
            return render(request, "index.html")
        else:
            return render(request, "login.html", {"msg": "用户名或密码错误! "})
    '''


# Django默认我们使用用户名和密码来登录，用Django提供的login，用于登陆验证，用user_login区分
'''def user_login(request):
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
'''


# 注册
class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, "register.html", {"register_form": register_form})

    def post(self, request):
        # 实例化form
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get("email", "")
            pass_word = request.POST.get("password", "")

            # 实例化一个user_profile对象，将前台值存入
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name

            # 默认激活状态为false
            user_profile.is_active = False

            # 加密password进行保存
            user_profile.password = make_password(pass_word)
            user_profile.save()

            # 发送注册激活邮件
            send_register_eamil(user_name, "register")

            # 跳转到登录页面
            return render(request, "login.html")
        else:
            return render(request, "register.html", {"register_form": register_form})


# 激活
class ActiveUserView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return HttpResponse("验证码已经失效")
        return render(request, "login.html")
