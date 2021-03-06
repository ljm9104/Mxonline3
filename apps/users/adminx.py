import xadmin
from django.contrib.auth.models import Permission, Group
# 和Xadmin的view绑定
from xadmin import views
from xadmin.models import Log

from users.models import EmailVerifyRecord, Banner, UserProfile
from organization.models import CityDict, CourseOrg, Teacher
from courses.models import Course, Lesson, Video, CourseResource
from operation.models import CourseComments, UserCourse, UserFavorite, UserMessage, UserAsk


class EmailVerifyRecordAdmin(object):
    list_display = ["code", "email", "send_type", "send_time"]
    search_fields = ["code", "email", "send_type"]
    list_filter = ["code", "email", "send_type", "send_time"]


class BannerAdmin(object):
    list_display = ["title", "image", "url", "index", "add_time"]
    search_fields = ["title", "image", "url", "index"]
    list_filter = ["title", "image", "url", "index", "add_time"]


class BaseSetting(object):
    # 开启主题功能
    enable_themes = True
    use_bootswatch = True


# xadmin 全局配置参数信息设置
class GlobalSettings(object):
    site_title = "雪竺轩: 慕课后台管理系统"
    site_footer = "ljm's mooc"
    # 收起菜单
    menu_style = "accordion"

    def get_site_menu(self):
        return (
            {"title": "机构管理", "menus": (
                {"title": "所在城市", "url": self.get_model_url(CityDict, "changelist")},
                {"title": "机构信息", "url": self.get_model_url(CourseOrg, "changelist")},
                {"title": "机构讲师", "url": self.get_model_url(Teacher, "changelist")},
            )},
            {"title": "课程管理", "menus": (
                {"title": "课程信息", "url": self.get_model_url(Course, "changelist")},
                {"title": "章节信息", "url": self.get_model_url(Lesson, "changelist")},
                {"title": "视频信息", "url": self.get_model_url(Video, "changelist")},
                {"title": "课程资源", "url": self.get_model_url(CourseResource, "changelist")},
                {"title": "课程评论", "url": self.get_model_url(CourseComments, "changelist")},
            )},

            {"title": "用户管理", "menus": (
                {"title": "用户信息", "url": self.get_model_url(UserProfile, "changelist")},
                {"title": "用户验证", "url": self.get_model_url(EmailVerifyRecord, "changelist")},
                {"title": "用户课程", "url": self.get_model_url(UserCourse, "changelist")},
                {"title": "用户收藏", "url": self.get_model_url(UserFavorite, "changelist")},
                {"title": "用户消息", "url": self.get_model_url(UserMessage, "changelist")},
            )},


            {"title": "系统管理", "menus": (
                {"title": "用户咨询", "url": self.get_model_url(UserAsk, "changelist")},
                {"title": "首页轮播", "url": self.get_model_url(Banner, "changelist")},
                {"title": "用户分组", "url": self.get_model_url(Group, "changelist")},
                {"title": "用户权限", "url": self.get_model_url(Permission, "changelist")},
                {"title": "日志记录", "url": self.get_model_url(Log, "changelist")},
            )},
        )


xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(Banner, BannerAdmin)
# 将全局配置管理与view绑定注册
xadmin.site.register(views.BaseAdminView, BaseSetting)
# 将头部与脚部信息进行注册:
xadmin.site.register(views.CommAdminView, GlobalSettings)
