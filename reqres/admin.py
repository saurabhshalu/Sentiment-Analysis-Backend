from django.contrib import admin
from .models import Searchres
from .models import Detailed


class SearchresAdmin(admin.ModelAdmin):
    list_display = ('hashtag','positive','negative','time1')

class DetailedResAdmin(admin.ModelAdmin):
    list_display = ('hashtag','time1','positive')

admin.site.register(Searchres,SearchresAdmin)
admin.site.register(Detailed,DetailedResAdmin)
# Register your models here.
