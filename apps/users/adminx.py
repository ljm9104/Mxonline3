import xadmin

from xadmin import views
from users.models import EmailVerifyRecord, Banner


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


# x admin 全局配置参数信息设置
class GlobalSettings(object):
    site_title = "学竺轩: 慕课后台管理站"
    site_footer = "ljm's imooc"
    # 收起菜单
    menu_style = "accordion"


xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(Banner, BannerAdmin)
# 将全局配置管理与view绑定注册
xadmin.site.register(views.BaseAdminView, BaseSetting)
# 将头部与脚部信息进行注册:
xadmin.site.register(views.CommAdminView, GlobalSettings)
