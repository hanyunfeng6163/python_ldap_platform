from django.contrib import admin

# Register your models here.
from accounts.models import User, UserLoginInfo, WebAuthorizationRecord, ExternalPermission


class UserInfoAdmin(admin.ModelAdmin):
    search_fields = ('username',)


admin.site.register(User, UserInfoAdmin)
admin.site.register(UserLoginInfo)
admin.site.register(WebAuthorizationRecord)
admin.site.register(ExternalPermission)
