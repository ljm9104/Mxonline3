from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View

from users.forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm
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
            # 用户查重
            if UserProfile.objects.filter(email=user_name):
                return render(request, "register.html", {"register_form": register_form, "msg": "用户已存在"})
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


# 忘记密码
class ForgetPwdView(View):
    def get(self, request):
        forget_from = ForgetForm()
        return render(request, "forgetpwd.html", {"forget_from": forget_from})

    # post方法实现
    def post(self, request):
        forget_form = ForgetForm(request.POST)
        # form验证合法情况下取出email
        if forget_form.is_valid():
            email = request.POST.get("email", "")
            # 发送找回密码邮件
            send_register_eamil(email, "forget")
            # 发送完毕返回登录页面并显示发送邮件成功。
            return render(request, "login.html", {"msg": "重置密码邮件已发送,请注意查收"})
        # 如果表单验证失败也就是他验证码输错等。
        else:
            return render(request, "forgetpwd.html", {"forget_from": forget_form})


# 重置密码
class ResetView(View):
    def get(self, request, active_code):
        all_record = EmailVerifyRecord.objects.filter(code=active_code)
        active_form = ActiveForm(request.GET)
        if all_record:
            for record in all_record:
                email = record.email
                return render(request, "password_reset.html", {"email": email})
        # 自己瞎输的验证码
        else:
            return render(request, "forgetpwd.html", {"msg": "您的重置密码链接无效,请重新请求", "active_form": active_form})


# 改变密码的view
class ModifyPwdView(View):
    def post(self, request):
        modiypwd_form = ModifyPwdForm(request.POST)
        if modiypwd_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            email = request.POST.get("email", "")
            # 如果两次密码不相等，返回错误信息
            if pwd1 != pwd2:
                return render(request, "password-reset.html", {"email": email, "msg": "密码不一致"})
            # 如果密码一致, 加密成密文, save保存到数据库
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()
            return render(request, "login.html", {"msg": "密码修改成功，请登录"})
        # 验证失败
        else:
            email = request.POST.get("email", "")
            return render(request, "password-reset.html", {"email": email, "modiypwd_form":modiypwd_form})
