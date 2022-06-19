from django.contrib import admin
from .models import ObjHandler, PopularChannel

class ObjHandlerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ObjHandler._meta.get_fields()]
    
class PopularChannelAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PopularChannel._meta.get_fields()]

admin.site.register(ObjHandler,ObjHandlerAdmin)
admin.site.register(PopularChannel,PopularChannelAdmin)
